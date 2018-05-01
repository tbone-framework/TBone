import React, {Component} from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import { Icon } from 'semantic-ui-react';

import {fetchUsers} from '../../actions/users';


const UserItem = (props) => (
    <li>
        <Icon 
            name={props.user.state ? 'circle' : 'circle thin'}
            size='small'
            color={props.user.state ? 'teal' : 'black'}
        />
        {props.user.username}
    </li>
)

class UserList extends Component {
    componentDidMount() {
        this.props.fetchUsers();   
    }

    render() {
        if (this.props.users === null)
            return <div className="parts-loading">
                <div>Loading parts...</div>
            </div>;

        const users=  Object.values(this.props.users.items).map((user, index) => {
            return (
                <UserItem
                    key={user._id}
                    user={user}
                    index={index}
                />
            );


        });
        if (users.length > 0)
            return (<ul className='user-list'>{users}</ul>);
        else
            return (<div>No users available</div>);
    }
}
;

function mapStateToProps(state) {
    return {users: state.users};
}

function mapDispatchToProps(dispatch) {
    return bindActionCreators({fetchUsers}, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(UserList);

