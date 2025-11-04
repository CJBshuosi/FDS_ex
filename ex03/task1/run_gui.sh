#!/bin/bash

# 运行 Chord GUI 应用程序的脚本
# 用法: ./run_gui.sh [--bits=<number>] [--dynamic=<true|false>]

cd "$(dirname "$0")"

# 默认参数
BITS=${1:-"--bits=3"}
DYNAMIC=${2:-"--dynamic=false"}

# 确保项目已编译
echo "编译项目..."
./gradlew build -x test -q

# 获取所有依赖的 JAR 文件
CLASSPATH="build/classes/java/main:build/resources/main"
for jar in $(find ~/.gradle/caches/modules-2/files-2.1 -name "*.jar" 2>/dev/null); do
    CLASSPATH="$CLASSPATH:$jar"
done

# 运行应用程序
echo "启动 Chord GUI 应用程序..."
echo "参数: $BITS $DYNAMIC"
java -cp "$CLASSPATH" ch.unibas.dmi.dbis.fds.p2p.ui.Main $BITS $DYNAMIC

