# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['media_downloader_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Media Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='Media Downloader.app',
    icon=None,
    bundle_identifier='com.mediadownloader.app',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'CFBundleName': 'Media Downloader',
        'CFBundleDisplayName': 'Media Downloader',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSPrincipalClass': 'NSApplication',
        'NSRequiresAquaSystemAppearance': 'No',
        'LSMinimumSystemVersion': '10.13.0',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeExtensions': ['*'],
                'CFBundleTypeName': 'All Files',
                'CFBundleTypeRole': 'Viewer',
            }
        ],
    },
)