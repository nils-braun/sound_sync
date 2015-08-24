#include <iostream>
#include "include/handler.h"





int main(int argc, char ** argv) {
    if(argc != 2) {
        std::cerr << "Usage: " << argv[0] << " port_number" << std::endl;
        exit(-1);
    }

    try {
        int port_number = std::stoi(argv[1]);
        handler::create_server(port_number).run();
    } catch (std::exception const & e) {
        std::cerr << e.what() << std::endl;
    }

    return 0;
}