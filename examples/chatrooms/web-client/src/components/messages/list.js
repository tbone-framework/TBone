import React, {Component} from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import { Feed, Icon, Grid, Divider } from 'semantic-ui-react';
import Moment from 'moment';

import Event from './event';
import './style.css';


const DayDividor = ({ts}) => {
    if(Moment(ts).isSame(Moment(), 'day'))
        var display = 'Today';
    else
        var display = Moment(ts).format('MMMM DD YYYY');
    return(
        <Feed.Event>
          <Feed.Content>
            <Feed.Summary>
                <Divider horizontal>{display}</Divider>
            </Feed.Summary>
          </Feed.Content>
        </Feed.Event>
    )
}

class MessageList extends Component{
    shouldComponentUpdate(nextProps, nextState){
        return !nextProps.messages.loading;
    }
    render(){
        let prev_ts=null, user=null, events = [], user_messages = [];
        const messages = Object.values(this.props.messages.entities).sort((a,b)=> a.created<b.created ? -1 : a.created>b.created ? 1 : 0);

        const addDay = msg => {
            events.push(<DayDividor key={msg.created.getTime()} ts={msg.created}/>);
            prev_ts =  msg.created;   
            user = null;         
        }

        for(let msg of messages){
            if(prev_ts===null)
                addDay(msg)
            if(!Moment(prev_ts).isSame(Moment(msg.created), 'day')){
                addDay(msg)
            }

            if(user===null){
                user = this.props.users[msg.user.id];
                events.push(<Event message={msg} user={user} pk={msg._id}/>);
            }else if(user._id !== msg.user.id){
                user = this.props.users[msg.user.id];
                events.push(<Event message={msg} user={user}/>);
            }else if(user._id === msg.user.id){
                let diff = Moment(msg.created).diff(Moment(prev_ts));
                if(diff-5 * 60 * 1000 > 0)
                    events.push(<Event message={msg} user={user}/>);
                else
                    events.push(<Event message={msg}/>);
            }
           prev_ts =  msg.created;      
        }
        return (
            <Grid className='message-list' columns={1} padded verticalAlign='bottom'>
                <Grid.Row>
                    <Grid.Column>
                        { events.length ?
                            <Feed className='message-list'>{events}</Feed>
                            :
                            <div>No events available</div>
                        }
                    </Grid.Column>
                </Grid.Row>
            </Grid>
        ); 
    };    
}


class Messages extends Component {
    shouldComponentUpdate(nextProps, nextState){
        // must update if the new selected channel is different
        if(this.props.channel !== nextProps.channel)
            return true; 

        if(this.props.channel===undefined || nextProps.channel === undefined)
            return false;
        // only update component if the there are new messages
        return this.props.channel.messages.unread != nextProps.channel.messages.unread;
    }
    render(){
        if(this.props.channel===undefined){
            return(<h2>Welcome To Team</h2>);
        }
        return(
            <div>
                <div className='loading'></div>
                <MessageList
                    messages={this.props.channel.messages}
                    users={this.props.users}
                />
            </div>
        );
    }
}

function mapStateToProps(state) {
    const channel = state.channels.entities[state.channels.selected];
    return {
        users: state.users.items,
        channel
    };
}

function mapDispatchToProps(dispatch) {
    //return bindActionCreators({fetchOrders, selectOrder}, dispatch);
    return {}
}

export default connect(mapStateToProps, mapDispatchToProps)(Messages);

