#include "../include/handler.h"

#include <cppcms/http_response.h>
#include <cppcms/http_context.h>
#include <cppcms/applications_pool.h>
#include <cppcms/http_request.h>
#include <cppcms/url_dispatcher.h>
#include <cppcms/url_mapper.h>
#include "../include/buffer_list.h"

handler::handler(cppcms::service &srv) : cppcms::application(srv)  {
    dispatcher().assign("/get/(\\d+)", &handler::get, this, 1);
    mapper().assign("get","/get/{1}");
    dispatcher().assign("/add", &handler::add, this);
    mapper().assign("add","/add");
}

cppcms::service & handler::create_server(const int port_number) {
    cppcms::json::value api_string;
    api_string.str("http");

    cppcms::json::value port_string;
    port_string.number(port_number);

    cppcms::json::object service_dict {{"api", api_string}, {"port", port_string}};
    cppcms::json::object settings_dict {{"service", service_dict}};

    static cppcms::service srv(settings_dict);
    srv.applications_pool().mount(cppcms::applications_factory<handler>());

    return srv;
}

void handler::get(std::string buffer_number_as_string) {
    try {
        std::string buffer = BufferList::getInstance().get(buffer_number_as_string);
        response().out() << buffer;
    } catch (const std::exception & e) {
        response().make_error_response(502, e.what());
    }
}

void handler::add() {
    const std::string & buffer = request().post("buffer");
    if(buffer != "") {
        BufferList::getInstance().add(buffer);
    }
}