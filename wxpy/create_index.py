'''
python3调用自定义的java类和方法建立索引
'''

import jnius_config
jnius_config.add_options('-Xrs', '-Xmx1024m')
jnius_config.set_classpath('.', 'C:\Program Files\java\jdk1.8.0_111\lib\*')
from jnius import autoclass

myclass = autoclass("jingyi.IndexMovies")
indexclass = myclass()
try:
    indexclass.Create_index()
except Exception as err:
    print(err)
finally:
    print("success")
