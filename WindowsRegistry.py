import sys
import _winreg as wreg
import cPickle as pickle

class WindowsRegistry:

    def __init__(self, company="RealVNC", project="WinVNC4", create=1):
        """
            Constructor to open registry key

            Returns: handle for registry access

            Examples:
            >>> r = WindowsRegistry('Microsoft', 'Windows')
            >>> isinstance(r, WindowsRegistry)
            True
            >>> r = WindowsRegistry('Santo Spirito', 'TestKey', create=1)
            >>> isinstance(r, WindowsRegistry)
            True
            
        """
        self.create = create
        self.company = company
        self.project = project
        self.keyname = "Software\\%s\\%s" % (self.company, self.project)

        rights = [ wreg.KEY_ALL_ACCESS, wreg.KEY_WRITE, wreg.KEY_READ, wreg.KEY_CREATE_SUB_KEY, wreg.KEY_SET_VALUE, wreg.KEY_ENUMERATE_SUB_KEYS, wreg.KEY_QUERY_VALUE ]
        rightsdict = {  wreg.KEY_ALL_ACCESS: 'KEY_ALL_ACCESS', wreg.KEY_WRITE: 'KEY_WRITE', wreg.KEY_READ: 'KEY_READ', wreg.KEY_QUERY_VALUE: 'KEY_QUERY_VALUE', wreg.KEY_SET_VALUE: 'KEY_SET_VALUE', wreg.KEY_CREATE_SUB_KEY: 'KEY_CREATE_SUB_KEY', wreg.KEY_ENUMERATE_SUB_KEYS: 'KEY_ENUMERATE_SUB_KEYS' }
        rights_writable = [ wreg.KEY_ALL_ACCESS, wreg.KEY_WRITE, wreg.KEY_CREATE_SUB_KEY, wreg.KEY_SET_VALUE ]
        self.key = None
        not_opened = True
        i=0
        while not_opened and i<len(rights)-1:
            try:
                self.key = wreg.OpenKey(wreg.HKEY_LOCAL_MACHINE, self.keyname,0, rights[0])
                not_opened = False
                self.right = rights[i]
                #print "rights = %05x" % rights[i]
                #print "Rights were: %s" % rightsdict[rights[i]]
            except Exception as e:
                if self.create:
                    self.key = wreg.CreateKey(wreg.HKEY_LOCAL_MACHINE, self.keyname)
                    not_opened = False
                #print "Error: ", sys.exc_info()[0]
                #print "%s" % e.strerror
                #print i
                #print "Tried rights = %s (0x%x)" % ( rightsdict[rights[i]], rights[i] )
                i=i+1

    def getval(self, name):
        """ Get value for key in registry """
        return wreg.QueryValueEx(self.key, name)
    
    def get_subkey(self, name):
        " Get subkey (Default) value out of registry "
        return wreg.QueryValue(self.key, name)

    def pget_subkey(self, name):
        " Get subkey (Default) value using pickle "
        return pickle.loads(self.get_subkey(name))
    
    def setval(self, name, value, value_type=wreg.REG_SZ):
        """
            Set value for key in registry

            Examples:
            >>> r.setval('test_stringval', 'string')
            >>> r.getval('test_stringval')
            (u'string', 1)
        """
        if not self.create and not self.right in rights_writable:
            raise Exception, "registry is read only"
        if value_type == wreg.REG_SZ:
            value = str(value)
        wreg.SetValueEx(self.key, name, 0, value_type, value)
        
    def set_subkey(self, subkey_name, value):
        """
            Set subkey (Default) value in registry

            Example:
            >>> r.set_subkey('test', 'test_str')
            >>> r.get_subkey('test')
            'test_str'
        """
        if not self.create and not self.right in rights_writable:
            raise Exception, "registry is read only"
        wreg.SetValue(self.key, subkey_name, wreg.REG_SZ, str(value))

    def pset_subkey(self, name, value):
        """
            Store python ojbect into subkey (Default) value using pickle

            Examples:
            >>> r.pset_subkey("testp_int", 123)
            >>> r.pget_subkey("testp_int")
            123
            >>> r.pset_subkey("testp_str", "string")
            >>> r.pget_subkey("testp_str")
            'string'
            >>> r.pset_subkey("testp_bool", True)
            >>> r.pget_subkey("testp_bool")
            True
            >>> r.pset_subkey("testp_float", 1.0)
            >>> r.pget_subkey("testp_float")
            1.0
            >>> r.pset_subkey("testp_complex", 1+1.0j)
            >>> r.pget_subkey("testp_complex")
            (1+1j)
            >>> r.pset_subkey("testp_unicode", u'unicodestr')
            >>> r.pget_subkey("testp_unicode")
            u'unicodestr'
            >>> r.pset_subkey("testp_tuple", (1, 2, 3, 'string'))
            >>> r.pget_subkey("testp_tuple")
            (1, 2, 3, 'string')
        """
        self.set_subkey(name, pickle.dumps(value))

    def del_subkey(self, subkey_name):
        """
            Delete the specified subkey

            Example:
            >>> r.pset_subkey('test_remove_subkey', 'removeme')
            >>> r.del_subkey('test_remove_subkey')
            >>> try:
            ...     r.pget_subkey('test_remove_subkey')
            ... except WindowsError:
            ...     print 'delete success'
            delete success
        """
        wreg.DeleteKey(self.key, subkey_name)
    def delval(self, name):
        """
            Delete the specified value

            Example:
            >>> r.setval('test_remove_stringval', 'removeme')
            >>> r.delval('test_remove_stringval')
            >>> try:
            ...     r.getval('test_remove_stringval')
            ... except WindowsError:
            ...     print 'delete success'
            delete success
        """
        wreg.DeleteValue(self.key, name)
    def close(self):
        """
            Close the key
        """
        if self.key:
            self.key.Close()

    def __del__(self):
        self.close()


if __name__=="__main__":
    import doctest
    try:
        r = WindowsRegistry('Santo Spirito', 'TestKey', create=1)
        # Run unit tests
        verbose=False
        doctest.testmod(None, None, None, verbose, True)
        r.del_subkey('test')
        r.del_subkey("testp_int")
        r.del_subkey("testp_str")
        r.del_subkey("testp_bool")
        r.del_subkey("testp_float")
        r.del_subkey("testp_complex")
        r.del_subkey("testp_unicode")
        r.del_subkey("testp_tuple")
        r.delval('test_stringval')
        # Cleanup the subkeys that the instance can't access
        wreg.DeleteKey(wreg.HKEY_LOCAL_MACHINE, r.keyname)
        wreg.DeleteKey(wreg.HKEY_LOCAL_MACHINE, 'Software\\Santo Spirito')
        r.close()
    except WindowsError as e:
        print e.strerror
        print "Try running as Administrator?"
