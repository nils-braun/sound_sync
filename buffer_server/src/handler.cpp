#include "../include/handler.h"

#include <cppcms/http_response.h>
#include <cppcms/http_context.h>
#include <cppcms/applications_pool.h>
#include <cppcms/http_request.h>
#include <cppcms/url_dispatcher.h>
#include <cppcms/url_mapper.h>

handler::handler(cppcms::service &srv) : cppcms::application(srv)  {
    dispatcher().assign("/get/(\\d+)", &handler::get, this, 1);
    mapper().assign("get","/get/{1}");
    dispatcher().assign("/start", &handler::getStart, this);
    mapper().assign("start","/start");
    dispatcher().assign("/add", &handler::add, this);
    mapper().assign("add","/add");
}

void handler::get(std::string buffer_number_as_string) {
    try {
        std::string buffer = m_bufferList.get(buffer_number_as_string);
        response().out() << buffer;
    } catch (const std::exception & e) {
        response().make_error_response(502, e.what());
    }
}

void handler::add() {
    const std::string & buffer = request().post("buffer");
    if(buffer != "") {
        m_bufferList.add(buffer);
    }
}

void handler::getStart() {
    const BufferList::BufferNumber startIndex = m_bufferList.getStartIndex();
    response().out() << static_cast<unsigned long int>(startIndex);
}

server::server(int port_number) {
    if(m_server != nullptr) {
        return;
    }

    cppcms::json::value api_string;
    api_string.str("http");

    cppcms::json::value port_string;
    port_string.number(port_number);
    std::cout << "C++" << port_number << std::endl;

    cppcms::json::object service_dict {{"api", api_string}, {"port", port_string}};
    cppcms::json::object settings_dict {{"service", service_dict}};

    m_server.reset(new cppcms::service(settings_dict));
    m_server->applications_pool().mount(cppcms::applications_factory<handler>());
}

void server::start() {
    if(m_server != nullptr) {
        std::cout << "start " << std::endl;
        m_server->run();
        std::cout << "end " << std::endl;
    }
}

void server::stop() {
    if(m_server != nullptr)
        m_server->shutdown();
    m_server.reset();
}