#pragma once
#include <cppcms/application.h>
#include <cppcms/service.h>

#include "../include/buffer_list.h"

class handler : public cppcms::application {
public:
    handler(cppcms::service &srv);

    void getBuffer(std::string buffer_number_as_string);
    void addBuffer();
    void getStartIndex();
    void getEndIndex();

private:
    BufferList m_bufferList;
};