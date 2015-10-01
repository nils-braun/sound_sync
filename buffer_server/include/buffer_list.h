#pragma once
#include <boost/python.hpp>

#include <deque>
#include <string>

class ValueErrorException: public std::exception
{
    virtual const char* what() const throw()
    {
        return "Wrong buffer index number";
    }
};

class BufferList {
public:
    typedef std::deque<std::string>::size_type BufferNumber;

    std::string get(const std::string & buffer_number_as_string) const;
    void add(const std::string & buffer);
    const BufferNumber getStartIndex() const;

private:
    const BufferNumber calculate_list_index(const BufferNumber buffer_number) const;

    std::deque<std::string> m_list = {};
    BufferNumber m_startIndex = 0;
    static constexpr BufferNumber maximumListIndex = 100;
};


BOOST_PYTHON_MODULE(buffer_list)
{
    boost::python::class_<BufferList>("BufferList")
        .def("get", &BufferList::get)
        .def("getStartIndex", &BufferList::getStartIndex)
        .def("add", &BufferList::add);
}