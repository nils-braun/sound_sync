#pragma once

#include <cppcms/application.h>
#include <cppcms/service.h>

class handler : public cppcms::application {
public:
    handler(cppcms::service &srv);

    void get(std::string buffer_number_as_string);
    void add();
    void start();

    static cppcms::service & create_server(const int port_number);
};