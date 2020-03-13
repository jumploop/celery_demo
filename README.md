# celery的python实践

### 简介

Celery是专注实时处理和任务调度的分布式任务队列。

>在程序的运行过程中，我们经常会碰到一些耗时耗资源的操作，为了避免它们阻塞主程序的运行，我们经常会采用多线程或异步任务。比如，在 Web 开发中，对新用户的注册，我们通常会给他发一封激活邮件，而发邮件是个 IO 阻塞式任务，如果直接把它放到应用当中，就需要等邮件发出去之后才能进行下一步操作，此时用户只能等待再等待。更好的方式是在业务逻辑中触发一个发邮件的异步任务，而主程序可以继续往下运行。
>Celery 是一个强大的分布式任务队列，它可以让任务的执行完全脱离主程序，甚至可以被分配到其他主机上运行。我们通常使用它来实现异步任务（async task）和定时任务（crontab）。它的架构组成如下图：

### 什么是任务队列

任务队列一般用于线程或计算机之间分配工作的一种机制。   

任务队列的输入是一个称为任务的工作单元，有专门的工作进行不断的监视任务队列，进行执行新的任务工作。

Celery 通过消息机制进行通信，通常使用中间人（Broker）作为客户端和职程（Worker）调节。启动一个任务，客户端向消息队列发送一条消息，然后中间人（Broker）将消息传递给一个职程（Worker），最后由职程（Worker）进行执行中间人（Broker）分配的任务。

Celery 可以有多个职程（Worker）和中间人（Broker），用来提高Celery的高可用性以及横向扩展能力

![Image](https://pic2.zhimg.com/80/v2-3cc47a82b844cca11c599250b4b491ae_720w.png)

<!-- ![Image](image\584bbf78e1783.png) -->

- 可以看到，Celery 主要包含以下几个模块：

    - 任务模块

        包含异步任务和定时任务。其中，异步任务通常在业务逻辑中被触发并发往任务队列，而定时任务由 Celery Beat 进程周期性地将任务发往任务队列。

    - 消息中间件 Broker

        Broker，即为任务调度队列，接收任务生产者发来的消息（即任务），将任务存入队列。Celery 本身不提供队列服务，官方推荐使用 RabbitMQ 和 Redis 等。

    - 任务执行单元 Worker

        Worker 是执行任务的处理单元，它实时监控消息队列，获取队列中调度的任务，并执行它。

    - 任务结果存储 Backend

        Backend 用于存储任务的执行结果，以供查询。同消息中间件一样，存储也可使用 RabbitMQ, Redis 和 MongoDB 等。


### 优点

- 简单

Celery 上手比较简单，不需要配置文件就可以直接运行。
它拥有一个庞大的社区，您可以在社区中进行交流问题，也可以通过 IRC 频道或邮件列表进行交流。
这是一个简单的 Demo：
```python
from celery import Celery

app = Celery('hello', broker='amqp://guest@localhost//')

@app.task
def hello():
    return 'hello world'
```
- 高可用

如果出现丢失连接或连接失败，职程（Worker）和客户端会自动重试，并且中间人通过 主/主 主/从 的方式来进行提高可用性。

- 快速

单个 Celery 进行每分钟可以处理数以百万的任务，而且延迟仅为亚毫秒（使用 RabbitMQ、 librabbitmq 在优化过后）。
- 灵活

Celery 的每个部分几乎都可以自定义扩展和单独使用，例如自定义连接池、序列化方式、压缩方式、日志记录方式、任务调度、生产者、消费者、中间人（Broker）等。


### celery的使用


- 准备工作

为了简单起见，对于 Broker 和 Backend，这里都使用 redis。在运行下面的例子之前，请确保 redis 已正确安装，并开启 redis 服务，当然，celery 也是要安装的。可以使用下面的命令来安装 celery 及相关依赖：
    
    pip install 'celery[redis]'

- 创建 Celery 实例

创建第一个 Celery 实例程序，我们把创建 Celery 程序成为 Celery 应用或直接简称 为 app，创建的第一个实例程序可能需要包含 Celery 中执行操作的所有入口点，例如创建任务、管理职程（Worker）等，所以必须要导入 Celery 模块。

```python
tasks.py
import time
from celery import Celery


broker = 'redis://127.0.0.1:6379'
backend = 'redis://127.0.0.1:6379/0'
app = Celery('tasks', broker = broker,backend=backend)
@app.task
def add(x, y):
    time.sleep(5) # 模拟耗时操作
    return x + y

```

- 上面的代码做了几件事：

    - 创建了一个 Celery 实例 app，名称为 tasks；
    - 指定消息中间件用 redis，URL 为 redis://127.0.0.1:6379；
    - 指定存储用 redis，URL 为 redis://127.0.0.1:6379/0；
    - 创建了一个 Celery 任务 add，当函数被 @app.task 装饰后，就成为可被 Celery 调度的任务；

- 启动 Celery Worker

在当前目录，使用如下方式启动 Celery Worker：

    celery worker -A tasks --loglevel=info

其中：

- 参数 -A 指定了 Celery 实例的位置，本例是在 tasks.py 中，Celery 会自动在该文件中寻找 Celery 对象实例，当然，我们也可以自己指定，在本例，使用 -A tasks.app；

- 参数 --loglevel 指定了日志级别，默认为 warning，也可以使用 -l info 来表示；  

关于 Celery 可用的命令完整列表，可以通过以下命令进行查看：

     celery worker --help

启动成功后，控制台会显示如下输出：

![Image](https://pic4.zhimg.com/80/v2-b8a48c4f6c6b870172e56047a9c07205.png)
<!-- ![Image](image\Snipaste_2020-03-13_17-03-09.png) -->

- 调用任务

需要调用我们创建的实例任务，可以通过 delay() 进行调用。

事实上，delay 方法封装了 apply_async，如下：

```python
    def delay(self, *args, **kwargs):
        """Star argument version of :meth:`apply_async`.

        Does not support the extra options enabled by :meth:`apply_async`.

        Arguments:
            *args (Any): Positional arguments passed on to the task.
            **kwargs (Any): Keyword arguments passed on to the task.
        Returns:
            celery.result.AsyncResult: Future promise.
        """
        return self.apply_async(args, kwargs)

    def apply_async(self, args=None, kwargs=None, task_id=None, producer=None,
                    link=None, link_error=None, shadow=None, **options):
        """Apply tasks asynchronously by sending a message.
```

delay() 是 apply_async() 的快捷方法，可以更好的控制任务的执行：

    >>> from tasks import add
    >>> add.delay(2, 2)
    <AsyncResult: 93b7812c-190b-4b24-ae3d-8ce0c7766838>
在上面，我们从 tasks.py 文件中导入了 add 任务对象，然后使用 delay() 方法将任务发送到消息中间件（Broker），Celery Worker 进程监控到该任务后，就会进行执行。我们将窗口切换到 Worker 的启动窗口，会看到多了两条日志：

![Image](https://pic4.zhimg.com/80/v2-1bfc0692304c4c3c75aec07bc6adb201.png)
<!-- ![Image](image\Snipaste_2020-03-13_17-05-06.png) -->

这说明任务已经被调度并执行成功。

另外，我们如果想获取执行后的结果，可以这样做：

    >>> result=add.delay(4,4)
    >>> result.ready()  # 使用 ready() 判断任务是否执行完毕
    True
    >>> result=add.delay(4,4)
    >>> result.ready()
    False
    >>> result.ready()
    True
    >>> result.get() # 使用 get() 获取任务结果
    8

通常我们是在应用程序中调用任务,将下面的代码保存为client.py文件：

```python
from tasks import add

# 异步任务
add.delay(2,2)

print("hello world")
```

运行命令 `python client.py`，可以看到，虽然任务函数 add 需要等待 5 秒才返回执行结果，但由于它是一个异步任务，不会阻塞当前的主程序，因此主程序会往下执行 print 语句，打印出结果。

### 使用配置

在上面的例子中，我们直接把 Broker 和 Backend 的配置写在了程序当中，更好的做法是将配置项统一写入到一个配置文件中，通常我们将该文件命名为 celeryconfig.py。Celery 的配置比较多，可以在官方文档查询每个配置项的含义。

下面，我们再看一个例子。项目结构如下：

    celery_demo                    # 项目根目录
        ├── celery_app             # 存放 celery 相关文件
        │   ├── __init__.py
        │   ├── celeryconfig.py    # 配置文件
        │   ├── task1.py           # 任务文件 1
        │   └── task2.py           # 任务文件 2
        └── client.py              # 应用程序

项目地址：https://github.com/jumploop/celery_demo

- 文件__init__.py代码如下：

```python

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/13 下午5:54
# @Author  : jumploop
# @File    : __init__.py
# @Software: PyCharm
from celery import Celery

app = Celery("demo")  # 创建 Celery 实例
app.config_from_object("celery_app.celeryconfig")  # 通过 Celery 实例加载配置模块
```

- 文件celeryconfig.py 代码如下：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/13 下午5:55
# @Author  : jumploop
# @File    : celeryconfig.py
# @Software: PyCharm
BROKER_URL = 'redis://127.0.0.1:6379/1'  # 指定 Broker(消息中间件来接收和发送任务消息)
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2'  # 指定 Backend(存储worker执行的结果)
# 指定时区,默认是 UTC
CELERY_TIMEZONE = 'Asia/Shanghai'
# CELERY_TIMEZONE='UTC'
# 指定任务的序列化
CELERY_TASK_SERIALIZER = 'json'
# 指定执行结果的序列化
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IMPORTS = (  # 指定导入的任务模块
    'celery_app.task1',
    'celery_app.task2'
)

```

- 文件task1.py 代码如下：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/13 下午5:55
# @Author  : jumploop
# @File    : task1.py
# @Software: PyCharm
from time import sleep
from celery_app import app


@app.task
def send_message(msg):
    sleep(5)  # 模拟耗时操作
    print(msg)
    return "message send ok"

```

- 文件task2.py 代码如下：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/13 下午5:55
# @Author  : jumploop
# @File    : task2.py
# @Software: PyCharm
from time import sleep
from celery_app import app


@app.task
def send_mail(data):
    sleep(5)  # 模拟耗时操作
    print(data)
    return "mail send ok"

```

- 文件client.py 代码如下：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/13 下午5:55
# @Author  : jumploop
# @File    : client.py
# @Software: PyCharm
from celery_app import task1
from celery_app import task2
# 执行异步任务的方式一:delay
task1.send_message.delay("hello world")
task2.send_mail.delay("hello celery")
# 执行异步任务的方式二:apply_async
task1.send_message.apply_async(args=("hello world",))
task2.send_mail.apply_async(args=("hello python",))

print("欢迎学习celery")

```

现在，让我们启动 Celery Worker 进程，在项目的根目录下执行下面命令：

    celery -A celery_app worker -l info

![Image](https://pic4.zhimg.com/80/v2-5b282da9b509128e0c6cfdc924567cab.png)
<!-- ![Imagge](image\Snipaste_2020-03-13_20-00-18.png) -->

接着，运行  `python3 client.py`，它会发送两个异步任务到 Broker，在 Worker 的窗口我们可以看到如下输出：

![Image](https://pic4.zhimg.com/80/v2-8069f9e92c1731b5e5eb670d632ed469.png)
<!-- ![Image](image\Snipaste_2020-03-13_22-17-37.png) -->

### 定时任务

Celery 除了可以执行异步任务，也支持执行周期性任务（Periodic Tasks），或者说定时任务。Celery Beat 进程通过读取配置文件的内容，周期性地将定时任务发往任务队列。

在原有项目上加上定时任务的配置:

```python
# schedules定时任务
CELERYBEAT_SCHEDULE = {
    'send_message-every-30-seconds': {
        'task': 'celery_app.task1.send_message',
        'schedule': timedelta(seconds=30),  # 每 30 秒执行一次
        'args': ("正在发送短信",)  # 任务函数参数
    },
    'send_mail-at-some-time': {
        'task': 'celery_app.task2.send_mail',
        'schedule': crontab(hour=22, minute=50),  # 每天晚上 22 点 50 分执行一次
        'args': ("正在发送邮件",)  # 任务函数参数
    }
}
```

现在，让我们启动 Celery Worker 进程，在项目的根目录下执行下面命令：

     celery worker -A celery_app  -l info

接着，启动 Celery Beat 进程，定时将任务发送到 Broker，在项目根目录下执行下面命令：

    celery beat -A celery_app

![Image](https://pic4.zhimg.com/80/v2-a02a1b6cafe1cdaa86deee6c059a0297.png)
<!-- ![Image](image\Snipaste_2020-03-13_22-47-07.png) -->

在上面，我们用两个命令启动了 Worker 进程和 Beat 进程，我们也可以将它们放在一个命令中：


    celery worker -B -A celery_app  -l info


之后，在 Worker 窗口我们可以看到，任务 task1 每 30 秒执行一次，而 task2 每天晚上 22 点 50 分执行一次。
![Image](https://pic4.zhimg.com/80/v2-7e79b720dc904326e72b779461909500.png)
<!-- ![Image](image\Snipaste_2020-03-13_22-59-17.png) -->

## 参考链接

- https://www.celerycn.io/ru-men/celery-chu-ci-shi-yong
- https://wiki.jikexueyuan.com/project/explore-python/Third-Party-Modules/celery.html
- http://docs.celeryproject.org/en/latest/userguide/configuration.html