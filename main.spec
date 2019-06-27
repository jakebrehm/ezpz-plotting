# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\brehm\\OneDrive\\Python\\EZPZ Offshoots\\EZPZ Baby Steps'],
             binaries=[],
             datas=[('Assets\\browse.png', 'assets'),
                    ('Assets\\checking.png', 'assets'),
                    ('Assets\\clear.png', 'assets'),
                    ('Assets\\controls.png', 'assets'),
                    ('Assets\\copy.png', 'assets'),
                    ('Assets\\icon.ico', 'assets'),
                    ('Assets\\logo.png', 'assets'),
                    ('Assets\\minus.png', 'assets'),
                    ('Assets\\paste.png', 'assets'),
                    ('Assets\\plot.png', 'assets'),
                    ('Assets\\plotting.png', 'assets'),
                    ('Assets\\plus.png', 'assets'),
                    ('Assets\\reading.png', 'assets'),
                    ('Assets\\tactair.bmp', 'assets'),
                    ('Assets\\yf.bmp', 'assets')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='EZPZ Plotting',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False , icon='Assets\\icon.ico')
