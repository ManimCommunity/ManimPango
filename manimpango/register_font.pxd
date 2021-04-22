
cdef extern from "fontconfig/fontconfig.h":
    ctypedef int FcBool
    ctypedef struct FcConfig:
        pass
    FcBool FcConfigAppFontAddFile(
        FcConfig* config,
        const unsigned char* file_name
    )
    FcConfig* FcConfigGetCurrent()
    void FcConfigAppFontClear(void *)

# Windows and macOS specific API's
IF UNAME_SYSNAME == "Windows":
    cdef extern from "windows.h":
        ctypedef Py_UNICODE WCHAR
        ctypedef const WCHAR* LPCWSTR
        ctypedef enum DWORD:
            FR_PRIVATE
        int AddFontResourceExW(
            LPCWSTR name,
            DWORD fl,
            unsigned int res
        )
        bint RemoveFontResourceExW(
            LPCWSTR name,
            DWORD  fl,
            unsigned int pdv
        )
ELIF UNAME_SYSNAME == "Darwin":
    cdef extern from "Carbon/Carbon.h":
        ctypedef struct CFURLRef:
            pass
        ctypedef enum CTFontManagerScope:
            kCTFontManagerScopeProcess
        ctypedef unsigned int UInt8
        ctypedef long CFIndex
        ctypedef unsigned int UInt32
        ctypedef UInt32 CFStringEncoding
        CFURLRef CFURLCreateWithBytes(
            void*,
            unsigned char *URLBytes,
            CFIndex length,
            CFStringEncoding encoding,
            void*
        )
        bint CTFontManagerRegisterFontsForURL(
            CFURLRef fontURL,
            CTFontManagerScope scope,
            void* error
        )
        bint CTFontManagerUnregisterFontsForURL(
            CFURLRef fontURL,
            CTFontManagerScope scope,
            void* error
        )
