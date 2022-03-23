[中文版](https://github.com/wey-gu/chinese-graph/blob/main/README-CN.md) | [English Version](https://github.com/wey-gu/chinese-graph)



## Setup the Knowledge Graph

### 1. Generate the data

```bash
$ python3 graph_data_generator.py
```

### 2. Load data to Nebula Graph Database

#### 2.1 Deploy Nebula Graph

> With Nebula-Up https://github.com/wey-gu/nebula-up/ it's just an one-liner to run

```bash
$ curl -fsSL nebula-up.siwei.io/install.sh | bash -s -- v3.0.0
```

You may see something like this:

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

#### 2.2 Load data into Nebula Graph

> With the help of Nebula-Importer https://github.com/vesoft-inc/nebula-importer/ in a Docker Image, it's also an one-liner call.

```bash
$ docker run --rm -ti \
    --network=nebula-docker-compose_nebula-net \
    -v ${PWD}/importer_conf.yaml:/root/importer_conf.yaml \
    -v ${PWD}/output:/root \
    vesoft/nebula-importer:v3.0.0 \
    --config /root/importer_conf.yaml
```

It'll take around 1 or 2 minutes to finish

> Connect to Nebula Graph with Nebula Console

Enter console:

```bash
$ ~/.nebula-up/console.sh # this is to start a container with console binary

# then call console to connect your Nebula Graph
$ nebula-console -addr graphd -port 9669 -user root -p nebula
```

Let's inspect some data in the graph!

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

(root@nebula) [chinese_idiom]> match p=(:idiom) return p limit 2
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

## Schema of the Graph
```sql
CREATE SPACE IF NOT EXISTS chinese_idiom(partition_num=5, replica_factor=1, vid_type=FIXED_STRING(24));
USE chinese_idiom;
# 创建点的类型
CREATE TAG idiom(pinyin string); #成语
CREATE TAG character(); #汉字
CREATE TAG character_pinyin(tone int); #单字的拼音
CREATE TAG pinyin_part(part_type string); #拼音的声部
# 创建边的类型
CREATE EDGE with_character(position int); #包含汉字
CREATE EDGE with_pinyin(position int); #读作
CREATE EDGE with_pinyin_part(part_type string); #包含声部
```