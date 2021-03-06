package com.test.user.thrift;

import com.test.thrift.data.DataService;
import org.apache.thrift.TServiceClient;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TFramedTransport;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import com.test.thrift.douban.DoubanService;

@Component
public class ServiceProvider {

    @Value("${thrift.spider.ip}")
    private String spiderServerIp;

    @Value("${thrift.spider.port}")
    private int spiderServerPort;

    @Value("${thrift.user.ip}")
    private String dataServerIp;

    @Value("${thrift.user.port}")
    private int dataServerPort;

    //声明枚举类型，完成服务类型的区分
    private enum ServiceType {
        SPIDER,
        USER
    }

    // 获取远程服务的代码 -> ip port 服务类型信息
    // 获取远程服务 == 返回类型 -- 泛型
    public <T> T getService(String ip, int port, ServiceType serverType) {
        // RPC框架时， 需要一个socket、transport、protocol， 服务端和客户端需要保持一致

        // 1. 声明一个Socket， 用来连接ServerSocket
        TSocket socket = new TSocket(ip, port, 3000);

        // 2. 生成一个传输方式对象 -- 基于 Socket 连接建立一个帧传输对象
        TTransport transport = new TFramedTransport(socket);
        // 开启帧传输
        try {
            transport.open();
        } catch (TTransportException e) {
            System.out.printf("开启帧传输时出现错误");
            e.printStackTrace();
            return null;
        }
        // 3. 指定传输发送的协议
        TProtocol protocol = new TBinaryProtocol(transport);

        // 4. 获取服务的客户端
        TServiceClient result = null;
        // 判断服务类型，并根据服务类型返回不同的客户端
        switch (serverType) {
            case USER:
                result = new DataService.Client(protocol);
                break;
            case SPIDER:
                result = new DoubanService.Client(protocol);
                break;
        }
        return (T) result;
    }

    //获取用户服务 ThriftServer 的用户客户端
    public DataService.Client getUserService() {
        return getService(dataServerIp, dataServerPort, ServiceType.USER);
    }

    public DoubanService.Client getDoubanService(){
        return getService(spiderServerIp,spiderServerPort,ServiceType.SPIDER);
    }


}
