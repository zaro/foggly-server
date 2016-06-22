import React from 'react';

export
function GenericTableHeaderRow() {
  return (
    <tr>
      <th>CommonTableHeaderRow</th>
    </tr>
  );
}

export
function GenericTableRow() {
  return (
    <tr>
      <td>CommonTableRow</td>
    </tr>
  );
}

export
class GenericTable extends React.Component {
  static defaultProps = {
    headerRowComponent: GenericTableHeaderRow,
    rowComponent: GenericTableRow,
    columns: 1,
  }
  static propTypes = {
    columns: React.PropTypes.number.isRequired,
  }

  constructor(props) {
    super(props);
    this.state = {
      dataList: [],
      loading: false,
    };
  }
  componentDidMount() {
    if (this.fetch) {
      this.fetch();
    }
  }
  componentWillUnmount() {
    if (this.cancelFetch) {
      this.cancelFetch();
    }
  }
  removeRow = (_id) => {
    const data = _.filter(this.state.dataList, (row) => _id !== row._id );
    this.setState({
      dataList: data,
    });
  }

  refreshData = () => {
    this.fetch();
  }

  render() {
    let spinner;
    if (this.state.loading) {
      spinner = (<tr>
        <td colSpan={this.props.columns} style={{ textAlign: 'center' }}>
          <i className="fa fa-spinner fa-3x fa-spin"></i>
        </td>
      </tr>);
    }
    return (
      <table className="table table-striped">
        <thead>
          <this.props.headerRowComponent {...this.props} />
        </thead>
        <tbody>
          {spinner}
          {this.state.dataList.map(
            (data) => <this.props.rowComponent {...data} {...this.props} key={data._id} removeRow={this.removeRow} refreshData={this.refreshData} />
          )}
        </tbody>
      </table>
    );
  }
}
