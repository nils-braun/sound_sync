#include <boost/python.hpp>

#include "../include/buffer_list.h"
#include "../include/handler.h"

BOOST_PYTHON_MODULE(buffer_server)
{
  boost::python::class_<server>("BufferServer", boost::python::init<int>())
    .def("start", &server::start)
    .def("stop", &server::stop);

  boost::python::class_<BufferList>("BufferList")
    .def("get", &BufferList::get)
    .def("getStartIndex", &BufferList::getStartIndex)
    .def("add", &BufferList::add);
}