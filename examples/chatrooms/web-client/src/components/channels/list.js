import React, {Component} from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import { Icon } from 'semantic-ui-react';
import {selectChannel, fetchChannels} from '../../actions/channels';
import './style.css';

const ChannelItem = (props) => (
    <li
        className= {props.selected ? 'selected' : ''}
        onClick={() => props.selectChannel() }
    >
        <Icon name={props.room.type === 20 ? 'lock' : 'hashtag'} size='small'/>
        {props.room.name}
    </li>
)

class ChannelList extends Component {
    componentDidMount() {
        this.props.fetchChannels();  
    }
    render() {
        if (this.props.channels.loading === true)
            return <div className="channels-loading">
                <div>Loading...</div>
            </div>;

        const rooms= this.props.channels.rooms.map((room_id, index) => {
            const room = this.props.channels.entities[room_id];
            return (
                <ChannelItem
                    key={room_id}
                    room={room}
                    index={index}
                    selectChannel={() => {
                        this.props.selectChannel(room);
                    }}
                    selected={this.props.channels.selected === room_id}
                />
            );

        });
        if (rooms.length > 0)
            return (<ul className='channel-list'>{rooms}</ul>);
        else
            return (<div>No rooms available</div>);
    }
}
;

function mapStateToProps(state) {
    return {channels: state.channels};
}

export default connect(mapStateToProps, {selectChannel, fetchChannels})(ChannelList);

