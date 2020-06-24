# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 23:45:59 2017

@author: yxl
"""
import os, sys
from ..engine import Macros, MkDown, Widget, Report
from sciapp import Source
from ... import root_dir
from codecs import open

def getpath(root, path):
    for i in range(10,0,-1):
        if not '../'*i in path: continue
        s = root
        for j in range(i):s=os.path.dirname(s)
        path = path.replace('../'*i, s+'/')
    return path.replace('\\\\','\\').replace('\\','/')

def extend_plugins(path, lst, err):
    rst = []
    for i in lst:
        if isinstance(i, tuple) or i=='-': rst.append(i)
        elif i[-3:] == 'rpt':
            pt = os.path.join(root_dir,path)
            rst.append(Report(i[:-4], pt+'/'+i))
            Source.manager('plugin').add(obj=rst[-1], name=rst[-1].title)
        elif i[-3:] in {'.md', '.mc', '.wf'}:
            p = os.path.join(os.path.join(root_dir, path), i).replace('\\','/')
            rst.append(Macros(i[:-3], ['Open>{"path":"%s"}'%p]))
            Source.manager('plugin').add(obj=rst[-1], name=rst[-1].title)
        elif i[-6:] in ['wgt.py', 'gts.py']:
            try:
                rpath = path.replace('/', '.').replace('\\','.')
                plg = __import__('imagepy.'+ rpath+'.'+i[:-3],'','',[''])
                if hasattr(plg, 'wgts'):
                    rst.extend([j if j=='-' else Widget(j) for j in plg.wgts])
                    for p in plg.wgts:
                        if not isinstance(p, str):Source.manager('widget').add(obj=p, name=p.title)
                else: 
                    rst.append(Widget(plg.Plugin))
                    Source.manager('widget').add(obj=plg.Plugin, name=plg.Plugin.title)
            except Exception as  e:
                err.append((path, i, sys.exc_info()[1]))
        else:
            try:
                rpath = path.replace('/', '.').replace('\\','.')
                plg = __import__('imagepy.'+ rpath+'.'+i[:-3],'','',[''])
                if hasattr(plg, 'plgs'):
                    rst.extend([j for j in plg.plgs])
                    for p in plg.plgs:
                        if not isinstance(p, str): Source.manager('plugin').add(obj=p, name=p.title)
                else: 
                    rst.append(plg.Plugin)
                    Source.manager('plugin').add(obj=plg.Plugin, name=plg.Plugin.title)
            except Exception as  e:
                err.append((path, i, sys.exc_info()[1]))
    return rst
            
def sort_plugins(catlog, lst):
    rst = []
    for i in catlog:
        if i=='-':rst.append('-')
        for j in lst:
            if j[:-3]==i or j[:-4]==i or j[0].title==i:
                lst.remove(j)
                rst.append(j)
    rst.extend(lst)
    return rst
        
def build_plugins(path, err='root'):
    root = err=='root'
    if root: err=[]
    subtree = []
    cont = os.listdir(os.path.join(root_dir, path))
    for i in cont:
        subp = os.path.join(path,i)
        if os.path.isdir(os.path.join(root_dir, subp)):
            sub = build_plugins(subp, err)
            if len(sub)!=0:subtree.append(sub[:2])
        elif i[-6:] in ('plg.py', 'lgs.py', 'wgt.py', 'gts.py'):
            subtree.append(i)
        elif i[-3:] in ('.mc', '.md', '.wf', 'rpt'):
            subtree.append(i)
    if len(subtree)==0:return []
    
    rpath = path.replace('/', '.').replace('\\','.')
    #rpath = rpath[rpath.index('imagepy.'):]
    pg = __import__('imagepy.'+rpath,'','',[''])
    pg.title = os.path.basename(path)
    if hasattr(pg, 'catlog'):
        subtree = sort_plugins(pg.catlog, subtree)
    subtree = extend_plugins(path, subtree, err)
    return pg, subtree, err
    
def extend_tools(path, lst, err):
    rst = []
    for i in lst:
        if i[-3:] in ('.mc', '.md', '.wf', 'rpt'):
            p = os.path.join(os.path.join(root_dir,path), i).replace('\\','/')
            rst.append((Macros(i[:-3], ['Open>{"path":"%s"}'%p]),
                os.path.join(root_dir, path)+'/'+i[:-3]+'.gif'))

            #rst.append((Macros(i[:-3], [getpath(pt, i) for i in cmds]),  
            #    os.path.join(root_dir, path)+'/'+i[:-3]+'.gif'))
        else:
            try:
                rpath = path.replace('/', '.').replace('\\','.')
                plg = __import__('imagepy.'+rpath+'.'+i,'','',[''])
                if hasattr(plg, 'plgs'): 
                    for i,j in plg.plgs: rst.append((i, path+'/'+j))
                else: rst.append((plg.Plugin, 
                    os.path.join(root_dir, path)+'/'+i.split('_')[0]+'.gif'))
            except Exception as e:
                err.append((path, i, sys.exc_info()[1]))
    for i in rst:Source.manager('tool').add(obj=i[0], name=i[0].title)
    return rst
            
def sort_tools(catlog, lst):
    rst = []
    for i in catlog:
        if i=='-':rst.append('-')
        for j in lst:
            if j==i or j[0].title==i or j[:-3]==i:
                lst.remove(j)
                rst.append(j)
    rst.extend(lst)
    return rst

def build_tools(path, err='root'):
    root = err=='root'
    if root: err=[]
    subtree = []
    cont = os.listdir(os.path.join(root_dir, path))

    for i in cont:
        subp = os.path.join(path,i)
        if root and os.path.isdir(os.path.join(root_dir, subp)):
            sub = build_tools(subp, err)
            if len(sub)!=0:subtree.append(sub[:2])
        elif not root:
            if i[len(i)-7:] in ('_tol.py', 'tols.py'):
                subtree.append(i[:-3])
            elif i[-3:] in ('.mc', '.md', '.wf', 'rpt'):
                subtree.append(i)
    if len(subtree)==0:return []
    rpath = path.replace('/', '.').replace('\\','.')
    #rpath = rpath[rpath.index('imagepy.'):]
    pg = __import__('imagepy.' + rpath,'','',[''])
    pg.title = os.path.basename(path)
    if hasattr(pg, 'catlog'):
        subtree = sort_tools(pg.catlog, subtree)
    if not root:subtree = extend_tools(path, subtree, err)    
    return pg, subtree, err
    
def extend_widgets(path, lst, err):
    rst = []
    for i in lst:
        try:
            rpath = path.replace('/', '.').replace('\\','.')
            plg = __import__('imagepy.'+rpath+'.'+i,'','',[''])
            rst.append(plg.Plugin)
        except Exception as e:
            err.append((path, i, sys.exc_info()[1]))
    for i in rst:Source.manager('widget').add(obj=i, name=i.title)
    return rst
            
def sort_widgets(catlog, lst):
    rst = []
    for i in catlog:
        if i=='-':rst.append('-')
        for j in lst:
            if j==i or j[:-3]==i or j[0].title==i:
                lst.remove(j)
                rst.append(j)
    rst.extend(lst)
    return rst
    
def build_widgets(path, err='root'):
    root = err=='root'
    if root: err=[]
    subtree = []
    cont = os.listdir(os.path.join(root_dir, path))
    for i in cont:
        subp = os.path.join(path,i)
        if root and os.path.isdir(os.path.join(root_dir, subp)):
            sub = build_widgets(subp, err)
            if len(sub)!=0:subtree.append(sub[:2])
        elif not root:
            if i[len(i)-7:] in ('_wgt.py', 'wgts.py'):
                subtree.append(i[:-3])
                #print('====', subtree)
    if len(subtree)==0:return []
    rpath = path.replace('/', '.').replace('\\','.')
    #rpath = rpath[rpath.index('imagepy.'):]
    pg = __import__('imagepy.' + rpath,'','',[''])
    pg.title = os.path.basename(path)
    if hasattr(pg, 'catlog'):
        subtree = sort_widgets(pg.catlog, subtree)
    if not root: subtree = extend_widgets(path, subtree, err)  
    return pg, subtree, err

def build_document(path):
    docs = []
    for lang in Source.manager('document').get('language'):
        for dirpath, dirnames, filenames in os.walk(path+'/'+lang):
            for filename in filenames:
                if filename[-3:] != '.md': continue
                docs.append(os.path.join(dirpath, filename))
                f = open(docs[-1], encoding='utf-8')
                cont = f.read()
                f.close()
                Source.manager('document').add(filename[:-3], cont, lang)
    return docs

def build_dictionary(path):
    for lang in Source.manager('dictionary').get('language'):
        for dirpath, dirnames, filenames in os.walk(path+'/'+lang):
            for filename in filenames:
                if filename[-3:] != 'dic': continue
                with open(os.path.join(dirpath, filename), encoding='utf-8') as f:
                    lines = f.read().replace('\r','').split('\n')
                dic = []
                for line in lines:
                    if line == '':
                        dic[-1] = (dic[-1][0][0], dict(dic[-1]))
                    elif line[0] == '\t':
                        dic[-1].append(line[1:].split('::'))
                    else:
                        dic.append([line.split('::')])
                if isinstance(dic[-1], list):
                    dic[-1] = (dic[-1][0][0], dict(dic[-1]))
                dic = dict(dic)
                for i in dic: 
                    obj = Source.manager('dictionary').get(i, tag=lang)
                    if not obj is None: obj.update(dic[i])
                    else: Source.manager('dictionary').add(i, dic[i], lang)
        common = Source.manager('dictionary').get('common', tag=lang)
        if common is None: return
        objs = Source.manager('dictionary').gets(tag=lang)
        for i in objs: i[1].update(common)

if __name__ == "__main__":
    print (os.getcwd())
    os.chdir('../../')
    data = build_tools('tools')