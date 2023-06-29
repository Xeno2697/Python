from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy as np

sourcefiles = ['/RED_guide/class/field.pyx']
setup(
    cmdclass = {'build_ext':build_ext},
    ext_modules = cythonize('field_compiled', sourcefiles)],
    include_dirs = [np.get_include()]
)
"""
sourcefiles:今回読み込みたいファイル。今回は上で書いたプログラムにcompute.pyxという名前を付けています。ファイルは複数個あっても大丈夫です。
setup:諸々の設定
* cmdclass : おまじない
* ext_modules :[Extension(このライブラリに付けたい名前、ライブラリのソースファイル)]。ソースファイルには上で定義したsourcefiles変数を渡すだけです。
* include_dirs : 使用しているライブラリのヘッダー。今回はnumpy(np)を使っているので、それをget_include()しています。
"""