# AGV_UI

## 软件运行

1. 仓库地址: `https://github.com/elephantrobotics/AGV_UI.git`
2. 分支管理:
   - `Raspberry Pi`版本的机器请克隆`Visualize_OP`分支
   - `Jetson Nano`版本的机器请克隆`Vis_JN`分支
   - 合并版本可以克隆`Vis_Merge`分支
3. 依赖安装: `pip install -r requirements.txt`
4. 运行软件: `python operations.py`

## 软件维护
### PyQT5 翻译家使用

1. 安装翻译家：`pip install pyqt5-tools`
2. 根据自己的安装路径配置系统环境
3. 需要翻译的文件
   - `operations.py`
   - `widgets/operation_ui.py`
   - `core/translate.py`
4. 翻译文件存放路径：`./assets/translation/operations_lang.ts`
5. 使用`pylupdate5`命令生成`.ts`文件
   ```shell
   # 添加翻译文件
   pylupdate5 -noobsolete .\operations.py .\widgets\operation_ui.py .\core\translate.py -ts .\assets\translation\operations_lang.ts
   ```
6. 使用`PyQT5-tools`自带的`QT Linguist`翻译`ts`文件
7. 翻译完成之后点击`发布`即可完成翻译
8. 安装
   ```shell
   sudo apt-get install ros-noetic-actionlib ros-noetic-actionlib-msgs
   ```