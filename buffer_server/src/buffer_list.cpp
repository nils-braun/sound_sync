#include "../include/buffer_list.h"

std::string BufferList::getBuffer(const std::string & bufferNumberAsString) const {
    BufferList::BufferNumber bufferNumber = static_cast<BufferList::BufferNumber>(std::stoll(bufferNumberAsString));
    const BufferNumber list_index = calculateListIndex(bufferNumber);
    return m_list[list_index];
}

void BufferList::addBuffer(const std::string & buffer) {
    m_list.push_back(buffer);

    if(m_list.size() > m_maximumListIndex) {
        m_list.pop_front();
        m_startIndex++;
    }
}

const BufferList::BufferNumber BufferList::getStartIndex() const {
    return m_startIndex;
}

const BufferList::BufferNumber BufferList::calculateListIndex(const BufferNumber bufferNumber) const {
    const BufferNumber list_index = bufferNumber - m_startIndex;

    if(list_index >= m_list.size() or list_index < 0) {
        throw ValueErrorException();
    }

    return list_index;
}
