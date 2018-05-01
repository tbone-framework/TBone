import React, {Component} from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import { Feed, Icon, Grid, Divider } from 'semantic-ui-react';
import Moment from 'moment';


const ChannelEntry = ({message, user}) => {
    const ts = Moment.utc(message.created).local().format('hh:mm A');
     return (
        <Feed.Event>
            <Feed.Label>
                { user ? <img src={user.avatar}/>  : null}
            </Feed.Label>
            <Feed.Content>
                { user ? 
                    <Feed.Summary>
                        <a>{user.username}</a>
                        <Feed.Date>{ts}</Feed.Date>
                    </Feed.Summary> : null
                }
                <Feed.Extra>
                    { message.text }
                </Feed.Extra>
            </Feed.Content>
        </Feed.Event>
    )   
}

export default ChannelEntry;