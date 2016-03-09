import React from 'react';
import apiCall from '../common/apicall';
import { ButtonInput, Modal, Input, Alert } from 'react-bootstrap';

export default class DomainAdd extends React.Component {
  constructor(props) {
     super(props);
     this.state = {
       showModal: true,
       working: false,
       valid: false,
       error: null
     };
  }
  show(){
    this.setState({ showModal: true, working: false, error: null })
  }
  close() {
    this.setState({ showModal: false, working: false })
    if(this.props.onClose){
      this.props.onClose();
    }
  }
  submit(e){
    e.preventDefault()
    this.addDomain()
  }

  addDomain() {
    this.setState({ working: true, error: null })
    let data = {
        domain: this.refs.domainName.getValue(),
        app_type: this.refs.appType.getValue(),
       }
    console.log('Adding domain:', data)
    apiCall('/api/domains/add',data, {method: "POST"})
      .then((data)=>{
        this.close()
      })
      .catch((data, error, textStatus)=>{
        console.log(data);
        console.log(textStatus);
        console.log(error);
        this.setState({ showModal: true, working: false, error: data.error })
      });

  }
  validate() {
    var domain = this.refs.domainName.getValue()
    var appType = this.refs.appType.getValue()
    this.setState({ valid: domain.length > 0 && appType.length > 0 })
  }
  render() {
    var spinner, error;
    if(this.state.working){
      spinner = <i className='fa fa-spinner fa-spin'></i>;
    }
    if(this.state.error && this.state.error.length){
      error =  <Alert bsStyle="danger">
        {this.state.error}
      </Alert>
    }
    return (
      <Modal show={this.state.showModal} onHide={(e) => this.close(e)}>
        <Modal.Header closeButton>
          <Modal.Title>Add domain {spinner}</Modal.Title>
          {error}
        </Modal.Header>
        <Modal.Body>
          <form onSubmit={(e)=> this.submit(e)}>
            <Input disabled={this.state.working} onChange={(e)=>this.validate()} label="Domain name" className="form-control" placeholder="Fully qualified domain name" ref="domainName" type="text" />
            <Input disabled={this.state.working} onChange={(e)=>this.validate()} type="select" label="Application type" ref="appType">
              <option key="no-app" value="">Select applicaiton type</option>
              {_.map(window.fConfig.appTypes,(v, k) =>{
                return <option key={k} value={k}>{v}</option>;
              })}
            </Input>
            <ButtonInput disabled={!this.state.valid} active type="submit" onClick={(e) => this.submit(e)} value="Submit"  bsStyle="default"/>
          </form>
        </Modal.Body>
        <Modal.Footer>
        </Modal.Footer>
      </Modal>
    );
  }
}
