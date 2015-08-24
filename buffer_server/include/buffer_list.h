#pragma once

#include <deque>

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

    static BufferList & getInstance() {
        static BufferList instance;
        return instance;
    }

private:
    BufferList() {}
    BufferList(const BufferList &) = delete;

public:
    const std::string & get(const std::string & buffer_number_as_string) const {
        BufferList::BufferNumber buffer_number = static_cast<BufferList::BufferNumber>(std::stoll(buffer_number_as_string));
        const BufferNumber list_index = calculate_list_index(buffer_number);
        return m_list[list_index];
    }

    const void add(const std::string & buffer) {
        m_list.push_back(buffer);

        std::cout << buffer << std::endl;

        if(m_list.size() > maximumListIndex) {
            m_list.pop_front();
        }
    }

private:
    const BufferNumber calculate_list_index(const BufferNumber buffer_number) const {
        const BufferNumber list_index = buffer_number - m_startIndex;

        if(list_index >= m_list.size() or list_index < 0) {
            throw ValueErrorException();
        }

        return list_index;
    }

    std::deque<std::string> m_list = {};
    BufferNumber m_startIndex = 0;
    static constexpr BufferNumber maximumListIndex = 100;
};