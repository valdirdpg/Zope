##############################################################################
#
# Zope Public License (ZPL) Version 0.9.5
# ---------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Any use, including use of the Zope software to operate a website,
#    must either comply with the terms described below under
#    "Attribution" or alternatively secure a separate license from
#    Digital Creations.  Digital Creations will not unreasonably
#    deny such a separate license in the event that the request
#    explains in detail a valid reason for withholding attribution.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# Attribution
# 
#   Individuals or organizations using this software as a web site must
#   provide attribution by placing the accompanying "button" and a link
#   to the accompanying "credits page" on the website's main entry
#   point.  In cases where this placement of attribution is not
#   feasible, a separate arrangment must be concluded with Digital
#   Creations.  Those using the software for purposes other than web
#   sites must provide a corresponding attribution in locations that
#   include a copyright using a manner best suited to the application
#   environment.  Where attribution is not possible, or is considered
#   to be onerous for some other reason, a request should be made to
#   Digital Creations to waive this requirement in writing.  As stated
#   above, for valid requests, Digital Creations will not unreasonably
#   deny such requests.
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
import ExtensionClass
import string
from string import strip, lower, upper, join
from Acquisition import Implicit
from Record import Record

record_classes={}

class SQLAlias(ExtensionClass.Base):
    def __init__(self, name): self._n=name
    def __of__(self, parent): return getattr(parent, self._n)
 
class NoBrains: pass

class Results:
    """Class for providing a nice interface to DBI result data
    """
    _index=None

    def __init__(self,(items,data),brains=NoBrains, parent=None):

        self._data=data
        self.__items__=items
        self._parent=parent
        self._names=names=[]
        self._schema=schema={}
        self._data_dictionary=dd={}
        aliases=[]
        i=0
        for item in items:
            name=item['name']
            name=strip(name)
            if not name:
                raise ValueError, 'Empty column name, %s' % name
            if schema.has_key(name):
                raise ValueError, 'Duplicate column name, %s' % name
            schema[name]=i
            n=lower(name)
            if n != name: aliases.append((n, SQLAlias(name)))
            n=upper(name)
            if n != name: aliases.append((n, SQLAlias(name)))
            dd[name]=item
            names.append(name)
            i=i+1

        self._nv=nv=len(names)
        
        # Create a record class to hold the records.
        names=tuple(names)
        if record_classes.has_key((names,brains)):
            r=record_classes[names,brains]
        else:
            class r(Record, Implicit, brains):
                'Result record class'               

            r.__record_schema__=schema
            for k in filter(lambda k: k[:2]=='__', Record.__dict__.keys()):
                setattr(r,k,getattr(Record,k))
                record_classes[names,brains]=r

            # Add SQL Aliases
            d=r.__dict__
            for k, v in aliases:
                if not hasattr(r,k): d[k]=v

            if hasattr(brains, '__init__'):
                binit=brains.__init__
                if hasattr(binit,'im_func'): binit=binit.im_func
                def __init__(self, data, parent, binit=binit):
                    Record.__init__(self,data)
                    binit(self.__of__(parent))

                r.__dict__['__init__']=__init__
                    
        self._class=r

        # OK, we've read meta data, now get line indexes

    def _searchable_result_columns(self): return self.__items__
    def names(self): return self._names
    def data_dictionary(self): return self._data_dictionary

    def __len__(self): return len(self._data)

    def __getitem__(self,index):
        if index==self._index: return self._row
        parent=self._parent
        fields=self._class(self._data[index], parent)
        self._index=index
        self._row=fields
        if parent is None: return fields
        return fields.__of__(parent)

    def asRDB(self): # Waaaaa
        r=[]
        append=r.append
        strings=[]
        nstrings=[]
        items=self.__items__
        indexes=range(len(items))
        join=string.join
        for i in indexes:
            item=items[i]
            t=lower(item['type'])
            if t=='s' or t=='t':
                t=='t'
                strings.append(i)
            else: nstrings.append(i)
            if item.has_key('width'): append('%s%s' % (item['width'], t))
            else: r.append(t)
                

        r=[join(self._names, '\t'), join(r,'\t')]
        append=r.append
        find=string.find
        split=string.split
        row=['']*len(items)
        tostr=str
        for d in self._data:
            for i in strings:
                v=tostr(d[i])
                if v:
                    if find(v,'\\') > 0: v=join(split(v,'\\'),'\\\\')
                    if find(v,'\t') > 0: v=join(split(v,'\t'),'\\t')
                    if find(v,'\n') > 0: v=join(split(v,'\n'),'\\n')
                row[i]=v
            for i in nstrings:
                row[i]=tostr(d[i])
            append(join(row,'\t'))
        append('')
                
        return join(r,'\n')
