#include "../include/server.h"
#include "../include/handler.h"

#include <cppcms/applications_pool.h>

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