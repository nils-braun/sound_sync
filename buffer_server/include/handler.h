#pragma once
#include <boost/python.hpp>

#include <cppcms/application.h>
#include <cppcms/service.h>

#include "../include/buffer_list.h"

class handler : public cppcms::application {
public:
    handler(cppcms::service &srv);

    void get(std::string buffer_number_as_string);
    void add();
    void start();

private:
    BufferList m_bufferList;
};

void start(int port_number);

BOOST_PYTHON_MODULE(buffer_server)
{
  boost::python::def("start", start);
}
