import os
import tempfile

# 必须在导入任何会触发 app.config / app.db 的模块之前指定临时库
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="wp-test-"))
