#include "../include/buffer_list.h"

std::string BufferList::get(const std::string & buffer_number_as_string) const {
    BufferList::BufferNumber buffer_number = static_cast<BufferList::BufferNumber>(std::stoll(buffer_number_as_string));
    const BufferNumber list_index = calculate_list_index(buffer_number);
    return m_list[list_index];
}

void BufferList::add(const std::string & buffer) {
    m_list.push_back(buffer);

    if(m_list.size() > maximumListIndex) {
        m_list.pop_front();
        m_startIndex++;
    }
}

const BufferList::BufferNumber BufferList::getStartIndex() const {
    return m_startIndex;
}

const BufferList::BufferNumber BufferList::calculate_list_index(const BufferNumber buffer_number) const {
    const BufferNumber list_index = buffer_number - m_startIndex;

    if(list_index >= m_list.size() or list_index < 0) {
        throw ValueErrorException();
    }

    return list_index;
}
