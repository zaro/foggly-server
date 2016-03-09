import React from 'react';
import taskPoll from '../common/taskpoll';
import { Button, Modal, Input } from 'react-bootstrap';

export default class DomainAdd extends React.Component {
  constructor(props) {
     super(props);
     this.state = {
       showModal: false,
       working: false
     };
  }
  show(){
    this.setState({
      showModal: true
    })
  }
  close() {
    this.setState({
      showModal: false
    })
  }
  add(e){
    e.preventDefault()
    this.setState({working: true})
  }

  render() {
    var spinner;
    if(this.state.working){
      spinner = <i className='fa fa-spinner fa-spin'></i>;
    }
    return (
      <Modal show={this.state.showModal} onHide={(e) => this.close(e)}>
        <Modal.Header closeButton>
          <Modal.Title>Add domain {spinner}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <form onSubmit={(e)=> this.add(e)}>
            <Input label="Domain name" className="form-control" placeholder="Fully qualified domain name" ref="domainName" type="text" />
            <Input type="select" label="Application type" placeholder="select" ref="appType">
              {_.map(window.fConfig.appTypes,(v, k) =>{
                return <option key={k} value={k}>{v}</option>;
              })}
            </Input>
            <Button active type="submit" className="pull-right" onClick={(e) => this.add(e)}>Add</Button>
          </form>
        </Modal.Body>
        <Modal.Footer>
        </Modal.Footer>
      </Modal>
    );
  }
}
