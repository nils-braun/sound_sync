/*
 * Server_test.cpp
 *
 *  Created on: 02.01.2015
 *      Author: nils
 */

#include "../Server.h"
#include "../Socket.h"
#include <sys/socket.h>
#include <pugixml.hpp>
#include <gtest/gtest.h>


class ServerTest : public testing::Test {
public:
	void SetUp() {
	}

	void TearDown() {
	}

	void SetUpClients() {
		struct sockaddr_in serverAddress;
		serverAddress.sin_addr.s_addr = INADDR_ANY;
		serverAddress.sin_port = htons(50007);
		serverAddress.sin_family = AF_INET;

		m_testSender = socket(PF_INET, SOCK_STREAM, 0);
		m_testListener = socket(PF_INET, SOCK_STREAM, 0);
		m_testUndefined = socket(PF_INET, SOCK_STREAM, 0);

		m_testServer.startListeningSteppwise();

		ASSERT_NE(connect(m_testSender, reinterpret_cast<struct sockaddr*>(&serverAddress), sizeof(serverAddress)), -1);
		ASSERT_NE(connect(m_testListener, reinterpret_cast<struct sockaddr*>(&serverAddress), sizeof(serverAddress)), -1);
		ASSERT_NE(connect(m_testUndefined, reinterpret_cast<struct sockaddr*>(&serverAddress), sizeof(serverAddress)), -1);

		m_testServer.mainLoop();
		m_testServer.mainLoop();
		m_testServer.mainLoop();
	}

	void SetUpEverything() {
		SetUpClients();

		sendMessage(m_testSender, "<client type='sender' name='testClient'><options frameRate='44100' waitingTime='500'/></client>");
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
		return(std::string(buffer).substr(0, bufferSize));
	}

	Server m_testServer;
	int m_testSender;
	int m_testListener;
	int m_testUndefined;
};

TEST_F(ServerTest, Listening) {

	m_testServer.startListeningSteppwise();

	int int_testClient = socket(PF_INET, SOCK_STREAM, 0);
	struct sockaddr_in serverAddress;
	serverAddress.sin_addr.s_addr = INADDR_ANY;
	serverAddress.sin_port = htons(50007);
	serverAddress.sin_family = AF_INET;
	ASSERT_NE(connect(int_testClient, reinterpret_cast<struct sockaddr*>(&serverAddress), sizeof(serverAddress)), -1);

	Socket testClient;
	ASSERT_NO_THROW(m_testServer.mainLoop());
	close(int_testClient);

	EXPECT_EQ(m_testServer.size(), 1);

}

TEST_F(ServerTest, ListeningMany) {

	m_testServer.startListeningSteppwise();

	int int_testClient[10];
	struct sockaddr_in serverAddress;
	serverAddress.sin_addr.s_addr = INADDR_ANY;
	serverAddress.sin_port = htons(50007);
	serverAddress.sin_family = AF_INET;

	for(int i = 0; i < 5; ++i) {
		int_testClient[i] = socket(PF_INET, SOCK_STREAM, 0);
		ASSERT_NE(connect(int_testClient[i], reinterpret_cast<struct sockaddr*>(&serverAddress), sizeof(serverAddress)), -1);
	}

	for(int i = 0; i < 5; ++i) {
		ASSERT_NO_THROW(m_testServer.mainLoop());
	}


	EXPECT_EQ(m_testServer.size(), 5);
}

TEST_F(ServerTest, ClientType) {
	SetUpClients();

	EXPECT_EQ(m_testServer.size(), 3);

	std::string helloMessage = "<client type='sender' name='testClient'><options frameRate='1587' waitingTime='6415'/></client>";

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

	std::string resultOptions = getMessage(m_testListener, 1024);
	result = doc.load_buffer(resultOptions.c_str(), resultOptions.size());
	ASSERT_EQ(result.status, pugi::xml_parse_status::status_ok);

	optionsNode = doc.first_child();

	ASSERT_STREQ("options", optionsNode.name());
	ASSERT_STREQ(optionsNode.attribute("frameRate").value(), "1587");
	ASSERT_STREQ(optionsNode.attribute("waitingTime").value(), "6415");
}

TEST_F(ServerTest, Transmission) {
	SetUpEverything();

	// TODO: Send and receive messages
}
