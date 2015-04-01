import numpy
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

extensions = [
    Extension("cy_sampler", ["cy_sampler.pyx"],
        include_dirs = [numpy.get_include()],
        extra_compile_args=["-O3"]
        ),
    #Extension("cy_feat_util", ["cy_feat_util.pyx"],
    #    include_dirs = [numpy.get_include()],
    #    language="c++",
    #    extra_compile_args=["-std=c++11"],
    #    extra_link_args=["-std=c++11"]
    #    ),
    #Extension("avper", ["avper.pyx"],
    #    include_dirs = [numpy.get_include()]
    #    ),        
]


setup(
    name = "cy_sampler",
    ext_modules = cythonize(extensions),
)
