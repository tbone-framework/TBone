import React, {Component} from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import { Icon, Menu, Input } from 'semantic-ui-react';

class TitleBar extends Component {
    render(){
        var title = null;
        if(this.props.channel)
            title = (<div><Icon name='hashtag'/>{this.props.channel.title}</div>);
        return(
            <Menu>
                <Menu.Item as='a' header>
                    <h3>{title}</h3>
                </Menu.Item>
                <Menu.Menu position='right'>
                    <Menu.Item>
                        <Input icon='search' placeholder='Search...' />
                    </Menu.Item>
              </Menu.Menu>
            </Menu> 
        )
    }
}

function mapStateToProps(state) {
    const channel = state.channels.entities[state.channels.selected];
    return {
        channel
    };
}

function mapDispatchToProps(dispatch) {
    //return bindActionCreators({selectRoom}, dispatch);
    return {}
}

export default connect(mapStateToProps, mapDispatchToProps)(TitleBar);