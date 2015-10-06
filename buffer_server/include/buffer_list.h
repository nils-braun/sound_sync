#pragma once
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

    BufferList(const BufferNumber maximumListIndex = 100) : m_maximumListIndex(maximumListIndex) { }

    std::string getBuffer(const std::string & bufferNumberAsString) const;
    void addBuffer(const std::string & buffer);
    const BufferNumber getStartIndex() const;
    void setStartIndex(const BufferNumber startIndex) {
        m_startIndex = startIndex;
    }

    const BufferNumber getNextFreeIndex() const {
        return m_startIndex + m_list.size();
    }

private:
    const BufferNumber calculateListIndex(const BufferNumber bufferNumber) const;

    std::deque<std::string> m_list = {};
    BufferNumber m_startIndex = 0;
    BufferNumber m_maximumListIndex;
};