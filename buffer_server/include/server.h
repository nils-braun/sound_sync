#pragma once
#include <cppcms/service.h>
#include <memory>

class server {
public:
    server(int port_number);
    void start();
    void stop();

private:
    std::shared_ptr<cppcms::service> m_server;
};
