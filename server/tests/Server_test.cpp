/*
 * Server_test.cpp
 *
 *  Created on: 02.01.2015
 *      Author: nils
 */

#include "Server.h"
#include "Socket.h"
#include <sys/socket.h>
#include <pugixml.hpp>
#include <gtest/gtest.h>
#include <sstream>


class ServerTest : public testing::Test {
public:
	std::streambuf *m_stdcout;
	std::streambuf *m_stdcerr;
	std::stringstream m_cout;
	std::stringstream m_cerr;

	void SetUp() override {
		echoOff();

		struct sockaddr_in * serverAddress = new struct sockaddr_in;
		serverAddress->sin_addr.s_addr = INADDR_ANY;
		serverAddress->sin_port = htons(50007);
		serverAddress->sin_family = AF_INET;
		m_serverAddress = reinterpret_cast<struct sockaddr*>(serverAddress);
	}

	void TearDown() override {
		echoOn();
		delete reinterpret_cast<struct sockaddr_in*>(m_serverAddress);
	}

	void echoOff() {

		m_stdcout = std::cout.rdbuf();
		m_stdcerr = std::cerr.rdbuf();
		std::cout.rdbuf(m_cout.rdbuf());
		std::cerr.rdbuf(m_cerr.rdbuf());
	}

	void echoOn() {
		std::cout.rdbuf(m_stdcout);
		std::cerr.rdbuf(m_stdcerr);
	}

	void SetUpClients() {
		m_testServer.startListeningSteppwise();

		connectToServer(m_testSender);
		connectToServer(m_testListener);
		connectToServer(m_testUndefined);

		m_testServer.mainLoop();
		m_testServer.mainLoop();
		m_testServer.mainLoop();
	}

	void SetUpEverything() {
		SetUpClients();

		sendMessage(m_testSender, "<client type='sender' name='testClient'><options frameRate='44100' waitingTime='500' soundDataSize='4.0'/></client>");
		sendMessage(m_testListener, "<client type='receiver' name='testClient'/>");

		m_testServer.mainLoop();

		getMessage(m_testListener, 1024);
	}

	void sendMessage(const int client, const std::string & message) {
		int numberOfBytesWritten = write(client, message.c_str(), message.size());
		EXPECT_EQ(numberOfBytesWritten, message.size());
	}

	std::string getMessage(const int client, const int bufferSize) {
		char buffer[bufferSize];
		int numberOfBytesRead = recv(client, buffer, sizeof(buffer), 0);
		EXPECT_LE(numberOfBytesRead, bufferSize);
		return(std::string(buffer).substr(0, numberOfBytesRead));
	}

	void connectToServer(int & int_testClient) {
		int_testClient = socket(PF_INET, SOCK_STREAM, 0);
		int connectionExitCode = connect(int_testClient, m_serverAddress, sizeof(*m_serverAddress));
		ASSERT_NE(connectionExitCode, -1);
	}

	Server m_testServer;
	int m_testSender;
	int m_testListener;
	int m_testUndefined;

private:
	struct sockaddr * m_serverAddress;
};

TEST_F(ServerTest, Listening) {

	// Start listening for one client
	m_testServer.startListeningSteppwise();

	// Setup test client and connect to server
	int int_testClient;
	connectToServer(int_testClient);

	// Receive connection from the connected client
	ASSERT_NO_THROW(m_testServer.mainLoop());
	EXPECT_EQ(m_testServer.size(), 1);

	close(int_testClient);
}

TEST_F(ServerTest, ListeningMany)
{
	m_testServer.startListeningSteppwise();

	unsigned int numberOfTestClients = 5;

	// Setup test clients
	std::vector<int> int_testClients;
	int_testClients.resize(numberOfTestClients);

	// Connect to server
	for(int int_testClient : int_testClients) {
		connectToServer(int_testClient);
	}

	// Receive connection from the connected client
	for(unsigned int counter = 0; counter < int_testClients.size(); counter++) {
		ASSERT_NO_THROW(m_testServer.mainLoop());
	}


	EXPECT_EQ(m_testServer.size(), 5);
}

TEST_F(ServerTest, ClientType) {
	SetUpClients();

	EXPECT_EQ(m_testServer.size(), 3);

	std::string helloMessage = "<client type='sender' name='testClient'><options frameRate='1587' waitingTime='6415' soundDataSize='4.0'/></client>";

	pugi::xml_document doc;
	pugi::xml_parse_result result = doc.load_buffer(helloMessage.c_str(), helloMessage.size());
	ASSERT_EQ(result.status, pugi::xml_parse_status::status_ok);

	pugi::xml_node rootNode = doc.first_child();
	pugi::xml_node optionsNode = rootNode.first_child();

	ASSERT_STREQ("client", rootNode.name());
	ASSERT_STREQ(rootNode.attribute("type").value(), "sender");
	ASSERT_STREQ(rootNode.attribute("name").value(), "testClient");

	ASSERT_STREQ("options", optionsNode.name());
	ASSERT_STREQ(optionsNode.attribute("frameRate").value(), "1587");
	ASSERT_STREQ(optionsNode.attribute("waitingTime").value(), "6415");
	ASSERT_STREQ(optionsNode.attribute("soundDataSize").value(), "4.0");

	sendMessage(m_testSender, helloMessage);

	helloMessage = "<client type='receiver' name='testClient'/>";

	result = doc.load_buffer(helloMessage.c_str(), helloMessage.size());
	ASSERT_EQ(result.status, pugi::xml_parse_status::status_ok);

	rootNode = doc.first_child();

	ASSERT_STREQ("client", rootNode.name());
	ASSERT_STREQ(rootNode.attribute("type").value(), "receiver");
	ASSERT_STREQ(rootNode.attribute("name").value(), "testClient");

	sendMessage(m_testListener, helloMessage);

	sendMessage(m_testUndefined, "bla bla");

	m_testServer.mainLoop();

	EXPECT_EQ(m_testServer.size(), 2);
	EXPECT_EQ(m_testServer.getFrameRate(), 1587);
	EXPECT_EQ(m_testServer.getWaitingTime(), 6415);
	EXPECT_EQ(m_testServer.getSoundDataSize(), 4);
	EXPECT_EQ(m_testServer.getSoundBufferSize(), int(1587*6415*4/1000.0));

	std::string resultOptions = getMessage(m_testListener, 1024);
	result = doc.load_buffer(resultOptions.c_str(), resultOptions.size());
	ASSERT_EQ(result.status, pugi::xml_parse_status::status_ok);

	optionsNode = doc.first_child();

	ASSERT_STREQ("options", optionsNode.name());
	ASSERT_STREQ(optionsNode.attribute("frameRate").value(), "1587");
	ASSERT_STREQ(optionsNode.attribute("waitingTime").value(), "6415");
}

TEST_F(ServerTest, NoSender) {
	SetUpClients();

	std::string helloMessage = "<client type='receiver' name='testClient'/>";

	pugi::xml_document doc;
	pugi::xml_parse_result result = doc.load_buffer(helloMessage.c_str(), helloMessage.size());
	ASSERT_EQ(result.status, pugi::xml_parse_status::status_ok);

	pugi::xml_node rootNode = doc.first_child();

	ASSERT_STREQ("client", rootNode.name());
	ASSERT_STREQ(rootNode.attribute("type").value(), "receiver");
	ASSERT_STREQ(rootNode.attribute("name").value(), "testClient");

	sendMessage(m_testListener, helloMessage);

	ASSERT_EQ(m_testServer.size(), 3);

	m_testServer.mainLoop();

	ASSERT_EQ(m_testServer.size(), 2);
}

TEST_F(ServerTest, Transmission) {
	SetUpEverything();
	int buffer_size_for_buffer_index = 8;

	ASSERT_EQ(m_testServer.size(), 3);

	const int bufferSize = 88200;
	char testBuffer[bufferSize];
	memset(testBuffer, 1, bufferSize);

	ASSERT_EQ(m_testServer.getSoundBufferSize(), bufferSize);

	int numberOfBytesWritten = 0;

	for(int i = 0; i < 20; i++) {
		numberOfBytesWritten += write(m_testSender, testBuffer, bufferSize);
	}
	ASSERT_EQ(numberOfBytesWritten, 20*bufferSize);

	for(int i = 0; i < 20; i++) {
		m_testServer.mainLoop();
	}

	close(m_testSender);

	m_testServer.mainLoop();

	ASSERT_EQ(m_testServer.size(), 2);

	char resultBuffer[bufferSize + buffer_size_for_buffer_index];
	memset(resultBuffer, 99, bufferSize + buffer_size_for_buffer_index);
	int numberOfBytesRead = read(m_testListener, resultBuffer, bufferSize + buffer_size_for_buffer_index);

	ASSERT_EQ(numberOfBytesRead, bufferSize + buffer_size_for_buffer_index);
	ASSERT_EQ(resultBuffer[0], '\x0');
	ASSERT_EQ(resultBuffer[1], 0);
	ASSERT_EQ(resultBuffer[2], 0);
	ASSERT_EQ(resultBuffer[3], 0);
	ASSERT_EQ(resultBuffer[buffer_size_for_buffer_index], 1);
	ASSERT_EQ(resultBuffer[8462], 1);

	memset(resultBuffer, 99, bufferSize + buffer_size_for_buffer_index);
	numberOfBytesRead = read(m_testListener, resultBuffer, bufferSize + buffer_size_for_buffer_index);

	ASSERT_EQ(numberOfBytesRead, bufferSize + buffer_size_for_buffer_index);
	ASSERT_EQ(resultBuffer[0], '\x1');
	ASSERT_EQ(resultBuffer[1], 0);
	ASSERT_EQ(resultBuffer[2], 0);
	ASSERT_EQ(resultBuffer[3], 0);
	ASSERT_EQ(resultBuffer[buffer_size_for_buffer_index], 1);
	ASSERT_EQ(resultBuffer[8462], 1);

	memset(resultBuffer, 99, bufferSize + buffer_size_for_buffer_index);
	numberOfBytesRead = read(m_testListener, resultBuffer, bufferSize + buffer_size_for_buffer_index);

	ASSERT_EQ(numberOfBytesRead, bufferSize + buffer_size_for_buffer_index);
	ASSERT_EQ(resultBuffer[0], '\x2');
	ASSERT_EQ(resultBuffer[1], 0);
	ASSERT_EQ(resultBuffer[2], 0);
	ASSERT_EQ(resultBuffer[3], 0);
	ASSERT_EQ(resultBuffer[buffer_size_for_buffer_index], 1);
	ASSERT_EQ(resultBuffer[8462], 1);

	memset(resultBuffer, 99, bufferSize + buffer_size_for_buffer_index);
	for(int i = 3; i < 20; i++) {
		numberOfBytesRead = read(m_testListener, resultBuffer, bufferSize + buffer_size_for_buffer_index);
		ASSERT_EQ(numberOfBytesRead, bufferSize + buffer_size_for_buffer_index);
	}

	ASSERT_EQ(resultBuffer[0], '\x13');
	ASSERT_EQ(resultBuffer[1], 0);
	ASSERT_EQ(resultBuffer[2], 0);
	ASSERT_EQ(resultBuffer[3], 0);
	ASSERT_EQ(resultBuffer[buffer_size_for_buffer_index], 1);
	ASSERT_EQ(resultBuffer[8462], 1);
}

TEST_F(ServerTest, TransmissionMany) {
	int buffer_size_for_buffer_index = 8;
	SetUpClients();

	sendMessage(m_testSender, "<client type='sender' name='testClient'><options frameRate='44100' waitingTime='500' soundDataSize='4.0'/></client>");
	sendMessage(m_testListener, "<client type='receiver' name='testClient'/>");

	m_testServer.mainLoop();

	getMessage(m_testListener, 1024);

	ASSERT_EQ(m_testServer.size(), 3);

	const int bufferSize = 88200;
	unsigned char testBuffer[bufferSize];
	unsigned char resultBuffer[bufferSize + buffer_size_for_buffer_index];

	ASSERT_EQ(m_testServer.getSoundBufferSize(), bufferSize);

	for(int j = 0; j < 1025; j++) {
		memset(testBuffer, 1, bufferSize);
		memset(resultBuffer, 99, bufferSize + buffer_size_for_buffer_index);

		int numberOfBytesWritten = write(m_testSender, testBuffer, bufferSize);
		ASSERT_EQ(numberOfBytesWritten, bufferSize);

		m_testServer.mainLoop();

		int numberOfBytesRead = read(m_testListener, resultBuffer, bufferSize + buffer_size_for_buffer_index);
		ASSERT_EQ(numberOfBytesRead, bufferSize + buffer_size_for_buffer_index);
		ASSERT_EQ(resultBuffer[0], j % 256);
		ASSERT_EQ(resultBuffer[1], j / 256);
		ASSERT_EQ(resultBuffer[2], 0);
		ASSERT_EQ(resultBuffer[3], 0);
		ASSERT_EQ(resultBuffer[buffer_size_for_buffer_index], 1);
		ASSERT_EQ(resultBuffer[8462], 1);
	}
}
