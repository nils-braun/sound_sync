#pragma once
#include <cppcms/application.h>
#include <cppcms/service.h>
#include <memory>

#include "../include/buffer_list.h"

class handler : public cppcms::application {
public:
    handler(cppcms::service &srv);

    void get(std::string buffer_number_as_string);
    void add();
    void getStart();

private:
    BufferList m_bufferList;
};

class server {
public:
    server(int port_number);
    void start();
    void stop();

private:
    std::shared_ptr<cppcms::service> m_server;
};
