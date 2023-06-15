CC?=gcc
TARGET=SimLiDAR

all:
	$(CC) main.c mysocket.c -o $(TARGET) -g
	$(CC) main.c mysocket.c -o $(TARGET)5 -g -DLASER_MODULE_NUM=5

clean:
	rm $(TARGET) $(TARGET)5
