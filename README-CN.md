[中文版](https://github.com/wey-gu/chinese-graph/blob/main/README-CN.md) | [English Version](https://github.com/wey-gu/chinese-graph)



## 搭建成语知识图谱

### 1. 收集、生成图谱数据

```bash
$ python3 graph_data_generator.py
```

### 2. 导入数据到 Nebula Graph 图数据库

#### 2.1 部署图数据库

> 借助于 Nebula-Up https://github.com/wey-gu/nebula-up/ ，一行就可以了。

```bash
$ curl -fsSL nebula-up.siwei.io/install.sh | bash -s -- v3.0.0
```

部署成功的话，会看到这样的结果：

```bash
┌────────────────────────────────────────┐
│ 🌌 Nebula-Graph Playground is Up now!  │
├────────────────────────────────────────┤
│                                        │
│ 🎉 Congrats! Your Nebula is Up now!    │
│    $ cd ~/.nebula-up                   │
│                                        │
│ 🌏 You can access it from browser:     │
│      http://127.0.0.1:7001             │
│      http://<other_interface>:7001     │
│                                        │
│ 🔥 Or access via Nebula Console:       │
│    $ ~/.nebula-up/console.sh           │
│                                        │
│    To remove the playground:           │
│    $ ~/.nebula-up/uninstall.sh         │
│                                        │
│ 🚀 Have Fun!                           │
│                                        │
└────────────────────────────────────────┘
```

#### 2.2 图谱入库

> 借助于 Nebula-Importer https://github.com/vesoft-inc/nebula-importer/ ，一行就可以了。

```bash
$ docker run --rm -ti \
    --network=nebula-docker-compose_nebula-net \
    -v ${PWD}/importer_conf.yaml:/root/importer_conf.yaml \
    -v ${PWD}/output:/root \
    vesoft/nebula-importer:v3.0.0 \
    --config /root/importer_conf.yaml
```

大概一两分钟数据就导入成功了，命令也会正常退出。

> 连到图数据库的 console

获得本机第一个网卡的地址，这里是 `10.1.1.168`

```bash
$ ip address

2: enp4s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 2a:32:4c:06:04:c4 brd ff:ff:ff:ff:ff:ff
    inet 10.1.1.168/24 brd 10.1.1.255 scope global dynamic enp4s0
```

进入 Console 的容器执行下边的命令：

```bash
$ ~/.nebula-up/console.sh

# nebula-console -addr 10.1.1.168 -port 9669 -user root -p nebula
```

检查一下导入的数据：

```sql
(root@nebula) [(none)]> show spaces
+--------------------+
| Name               |
+--------------------+
| "chinese_idiom"    |
+--------------------+

(root@nebula) [(none)]> use chinese_idiom
Execution succeeded (time spent 1510/2329 us)

Fri, 25 Feb 2022 08:53:11 UTC

(root@nebula) [chinese_idiom]> match p=(成语:idiom) return p limit 2
+------------------------------------------------------------------+
| p                                                                |
+------------------------------------------------------------------+
| <("一丁不识" :idiom{pinyin: "['yi1', 'ding1', 'bu4', 'shi2']"})> |
| <("一丝不挂" :idiom{pinyin: "['yi1', 'si1', 'bu4', 'gua4']"})>   |
+------------------------------------------------------------------+

(root@nebula) [chinese_idiom]> SUBMIT JOB STATS
+------------+
| New Job Id |
+------------+
| 11         |
+------------+
(root@nebula) [chinese_idiom]> SHOW STATS
+---------+--------------------+--------+
| Type    | Name               | Count  |
+---------+--------------------+--------+
| "Tag"   | "character"        | 4847   |
| "Tag"   | "character_pinyin" | 1336   |
| "Tag"   | "idiom"            | 29503  |
| "Tag"   | "pinyin_part"      | 57     |
| "Edge"  | "with_character"   | 116090 |
| "Edge"  | "with_pinyin"      | 5943   |
| "Edge"  | "with_pinyin_part" | 3290   |
| "Space" | "vertices"         | 35739  |
| "Space" | "edges"            | 125323 |
+---------+--------------------+--------+
```

