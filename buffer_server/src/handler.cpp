#include "../include/handler.h"

#include <cppcms/http_response.h>
#include <cppcms/http_context.h>
#include <cppcms/http_request.h>
#include <cppcms/url_dispatcher.h>
#include <cppcms/url_mapper.h>

handler::handler(cppcms::service &srv) : cppcms::application(srv)  {
    dispatcher().assign("/get/(\\d+)", &handler::getBuffer, this, 1);
    mapper().assign("get","/get/{1}");
    dispatcher().assign("/start", &handler::getStartIndex, this);
    mapper().assign("start","/start");
    dispatcher().assign("/end", &handler::getEndIndex, this);
    mapper().assign("end","/end");
    dispatcher().assign("/add", &handler::addBuffer, this);
    mapper().assign("add","/add");
}

void handler::getBuffer(std::string buffer_number_as_string) {
    try {
        std::string buffer = m_bufferList.getBuffer(buffer_number_as_string);
        response().out() << buffer;
    } catch (const std::exception & e) {
        response().make_error_response(502, e.what());
    }
}

void handler::addBuffer() {
    const std::string & buffer = request().post("buffer");
    if(buffer != "") {
        m_bufferList.addBuffer(buffer);
    }
}

void handler::getStartIndex() {
    const BufferList::BufferNumber startIndex = m_bufferList.getStartIndex();
    response().out() << static_cast<unsigned long int>(startIndex);
}

void handler::getEndIndex() {
    const BufferList::BufferNumber nextFreeAddressIndex = m_bufferList.getNextFreeIndex();
    if(nextFreeAddressIndex == 0) {
        response().out() << static_cast<unsigned long int>(nextFreeAddressIndex);
    } else {
        response().out() << static_cast<unsigned long int>(nextFreeAddressIndex - 1);
    }
}