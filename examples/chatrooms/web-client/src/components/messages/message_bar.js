import React, {Component} from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import { Form, Icon } from 'semantic-ui-react';

import { sendMessage } from '../../actions/messages';

const sideBarWidth = '200px';

const style = {
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
}

class MessageBar extends Component {

    constructor(props){
        super(props);
        this.state = {message: ''};
    
        this.onKeyPress = this.onKeyPress.bind(this);
        // this.onInputChange = this.onInputChange.bind(this);
        this.onFormSubmit = this.onFormSubmit.bind(this);
    }
    onFormSubmit(event){
        event.preventDefault();
        this.props.sendMessage(this.props.channel, this.state.message);
        // reset the term
        this.setState({message: ''});
    }
    onKeyPress(event){
        if(event.key=='Enter' && event.shiftKey == false){
            this.onFormSubmit(event);
        }
    }
    render(){
        return(
            <Form
                onSubmit={this.onFormSubmit} 
                id='message-form'
            > 
                <Form.Group style={{margin:0}}>
                    <div style={{backgroundColor: 'white', color:'#aaa', padding: '10px'}}><Icon name='plus'/></div>
                    <Form.TextArea 
                        width={15}
                        autoHeight
                        form='message-form'
                        placeholder='Enter message here'
                        style={style.textArea}
                        rows={1}
                        value={this.state.message}
                        onKeyPress = {this.onKeyPress}
                        onChange = {(event, data) => {
                            this.setState({message: event.target.value});
                            console.log(event.target.value);
                        }}
                    />
                    <Form.Button basic icon color='grey' size='large'><Icon name='smile'/></Form.Button>
                </Form.Group>
            </Form>
        )
    }
}

function mapStateToProps(state) {
    const channel = state.channels.entities[state.channels.selected];
    return { channel };
}

export default connect(mapStateToProps, {sendMessage})(MessageBar);