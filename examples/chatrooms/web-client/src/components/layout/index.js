
import React from 'react'
import { Container } from 'semantic-ui-react';

import SideBar from '../sidebar';
import RoomList from '../channels/list';
import UserList from '../users/list';
import TitleBar from './title_bar';
import Messages from '../messages/list';
import MessageBar from '../messages/message_bar';


import './style.css';

const sideBarWidth = '200px';
const style = {
    container:{
        height:'inherit'
    },
    side: {
        position: 'fixed',
        top: 0,
        left: 0,
        bottom: 0,
        width: sideBarWidth,
        backgroundColor: '#4c384b',
        padding: '20px 0',
        lineHeight: '25px',
        color: '#cac4c9',
        title:{
            padding: '0 20px',
            color: 'white'
        }
    },
    main: {
        marginLeft: sideBarWidth,
        marginRight: sideBarWidth,
        position: 'relative',
        height:'inherit'
    },
    rightSide: {
        position: 'absolute',
        top: 0,
        right: 0,
        bottom: 0,
        width: sideBarWidth,
        backgroundColor: '#0ff',
    },
    msgInput: {
        border: '2px solid #a1a2a3',
        borderRadius: '4px',
        boxSizing: 'border-box',
        position: 'fixed',
        left: sideBarWidth,
        bottom: 0,
        right: sideBarWidth,
        margin: '15px 0px',
        padding: 0,
        textArea : {
            border: 0,
            borderLeft: '2px solid #a1a2a3',
            borderRadius: 0,
            margin: 0,
            boxSizing: 'border-box'
        },
    },
}

const Layout = () => (
  <div className='workspace-container' style={style.container}>
    <aside style={style.side}>
        <h3 style={style.side.title}>Chatrooms</h3>
        <div style={{padding: '0 20px'}}>Channels</div>
        <RoomList/>
        <div style={{padding: '0 20px'}}>Users</div>
        <UserList/>
    </aside>
    {/*
    <div className='main' style={style.main}>
        <Container fluid style={{height: '100%'}}>
            <TitleBar/>
            <Messages/>
        </Container>
        <MessageBar/>
    </div>
    */}
    <div className='main'>
        <TitleBar className='message-header'/>
        <div className='messages'>
            <Messages/>
        </div>
        <MessageBar className='message-bar'/>
    </div>

    {/*
    <div style={style.rightSide}>
        stuff
    </div>
    */}
  </div>
)

export default Layout;