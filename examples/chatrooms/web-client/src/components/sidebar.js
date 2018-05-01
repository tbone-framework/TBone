import React, { Component } from 'react'
import { Sidebar, Segment, Menu, Input} from 'semantic-ui-react'


const style = {
  height: '500px'
}

const MainMenu = () => (
    <Menu pointing>
        <Menu.Item name="unitInfo" active={true}>Unit Info</Menu.Item>
        <Menu.Item name="pilots" active={false}>Pilots</Menu.Item>
        <Menu.Item name="mechs" active={false}>Mechs</Menu.Item>
        <Menu.Item name="unitOrganization" active={false}>Unit Organization</Menu.Item>
        <Menu.Menu position='right'>
        <Menu.Item>
            <Input icon='search' placeholder='Search...' />
        </Menu.Item>
      </Menu.Menu>
    </Menu>    
)

class RoomSideBar extends Component {
  state = { visible: true }

  toggleVisibility = () => this.setState({ visible: !this.state.visible })

  render() {
    const { visible } = this.state
    return (
      <div style={style}>
        <Sidebar.Pushable as={Segment}>
          <Sidebar as={Menu} animation='uncover' width='thin' visible={visible} icon='labeled' vertical inverted>
          </Sidebar>
          <Sidebar.Pusher>
            <Segment basic>
            </Segment>
          </Sidebar.Pusher>
        </Sidebar.Pushable>
      </div>
    )
  }
}

export default RoomSideBar