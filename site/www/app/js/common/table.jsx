import React from 'react';
import apiCall from '../common/apicall';

export
class GenericTableHeaderRow extends React.Component {
  render() {
    return (
      <tr>
        <th>CommonTableHeaderRow</th>
      </tr>
    )
  }
}

export
class GenericTableRow extends React.Component {
  constructor(props) {
    super(props);
  }
  render() {
    return (
      <tr>
        <td>CommonTableRow</td>
      </tr>
    );
  }
}

export
class GenericTable extends React.Component {
  static defaultProps  = {
    headerRowComponent: GenericTableHeaderRow,
    rowComponent: GenericTableRow,
    columns: 1,
  }
  constructor(props) {
    super(props);
    this.state = {
      dataList: [],
      loading: false,
    }
  }
  componentDidMount() {
    if(this.fetch){
      this.fetch()
    }
  }
  componentWillUnmount() {
    if (this.cancelFetch) {
      tthis.cancelFetch();
    }
  }
  removeRow(_id) {
    let data = _.filter(this.state.dataList,(row)=>{
      return _id !== row._id
    });
    this.setState({
      dataList : data,
    })
  }
  render() {
    var createRow = (data) => {
      return <this.props.rowComponent {...data} key={data._id} removeRow={(_id)=>this.removeRow(_id)}/>;
    };
    var spinner;
    if (this.state.loading) {
      spinner = <tr>
        <td colSpan={this.props.columns} style={{
          textAlign: "center"
        }}>
          <i className='fa fa-spinner fa-3x fa-spin'></i>
        </td>
      </tr>;
    }
    return (
      <table className="table table-striped">
        <thead>
          <this.props.headerRowComponent {...this.props} />
        </thead>
        <tbody>
          {spinner}
          {this.state.dataList.map(createRow)}
        </tbody>
      </table>
    );
  }
}
