"""主程序入口"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import PlumForestQT


def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = PlumForestQT()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()