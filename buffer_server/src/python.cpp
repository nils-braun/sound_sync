#include <boost/python.hpp>

#include "../include/buffer_list.h"
#include "../include/handler.h"
#include "../include/server.h"

BOOST_PYTHON_MODULE(buffer_server)
{
  boost::python::class_<server>("BufferServer", boost::python::init<int>())
    .def("start", &server::start)
    .def("stop", &server::stop);

  boost::python::class_<BufferList>("BufferList", boost::python::init<unsigned int>())
    .def("get_buffer", &BufferList::getBuffer)
    .def("get_start_index", &BufferList::getStartIndex)
    .def("set_start_index", &BufferList::setStartIndex)
    .def("get_next_free_index", &BufferList::getNextFreeIndex)
    .def("add_buffer", &BufferList::addBuffer);
}