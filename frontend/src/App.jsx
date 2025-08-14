import { useState } from 'react';
import axios from 'axios';
import {
  Layout,
  Form,
  Input,
  InputNumber,
  Button,
  ColorPicker,
  Spin,
  Alert,
  Row,
  Col,
  Card,
  Typography,
  notification,
  Space,
} from 'antd';

const { Header, Content } = Layout;
const { Title } = Typography;
const { TextArea } = Input;

function App() {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const handleGeneratePdf = async (values) => {
    const {
      fens,
      diagramsPerPage,
      padding,
      lightSquares,
      darkSquares,
      borderColor,
      singleColumn,
      twoColumnMax,
    } = values;

    const fenList = fens.split('\n').filter((fen) => fen.trim() !== '');
    if (fenList.length === 0) {
      notification.error({
        message: 'Validation Error',
        description: 'Please enter at least one FEN string.',
      });
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(
        '/api/generate-pdf/',
        {
          fens: fenList,
          diagrams_per_page: diagramsPerPage,
          padding: {
            top: padding,
            bottom: padding,
            left: padding,
            right: padding,
          },
          board_colors: {
            light_squares: lightSquares,
            dark_squares: darkSquares,
            border_color: borderColor,
          },
          columns_for_diagrams_per_page: {
            single_column: singleColumn,
            two_column_max: twoColumnMax,
          },
        },
        {
          responseType: 'blob',
        }
      );

      const file = new Blob([response.data], { type: 'application/pdf' });
      const fileURL = URL.createObjectURL(file);

      const link = document.createElement('a');
      link.href = fileURL;
      link.setAttribute('download', 'chess_diagrams.pdf');
      document.body.appendChild(link);
      link.click();

      link.parentNode.removeChild(link);
      URL.revokeObjectURL(fileURL);

      notification.success({
        message: 'PDF Generated',
        description: 'Your chess diagram PDF has been successfully generated.',
      });
    } catch (err) {
      const errorData = err.response?.data;
      const errorMessage =
        errorData && typeof errorData === 'object'
          ? JSON.stringify(errorData)
          : 'An unexpected error occurred. Please check the console for more details.';

      notification.error({
        message: 'Error Generating PDF',
        description: errorMessage,
        duration: 10,
      });

      console.error('Full error object:', err);
      if (err.response) {
        console.error('Error response data:', err.response.data);
        console.error('Error response status:', err.response.status);
        console.error('Error response headers:', err.response.headers);
      } else if (err.request) {
        console.error('Error request:', err.request);
      } else {
        console.error('Error message:', err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <Title level={2} style={{ color: 'white', lineHeight: '64px', margin: 0 }}>
          Chess Diagram PDF Generator
        </Title>
      </Header>
      <Content style={{ padding: '24px' }}>
        <Row justify="center">
          <Col xs={24} sm={20} md={16} lg={12} xl={10}>
            <Card>
              <Spin spinning={loading} tip="Generating PDF...">
                <Form
                  form={form}
                  layout="vertical"
                  onFinish={handleGeneratePdf}
                  initialValues={{
                    fens: '',
                    diagramsPerPage: 6,
                    padding: 5,
                    lightSquares: '#f0d9b5',
                    darkSquares: '#b58863',
                    borderColor: '#ffffffff',
                    singleColumn: 1,
                    twoColumnMax: 8,
                  }}
                >
                  <Form.Item
                    name="fens"
                    label="Enter FEN strings (one per line):"
                    rules={[
                      {
                        required: true,
                        message: 'Please input at least one FEN string!',
                      },
                    ]}
                  >
                    <TextArea
                      rows={10}
                      placeholder="e.g., rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
                      style={{ fontFamily: "'Courier New', Courier, monospace" }}
                    />
                  </Form.Item>

                  <Row gutter={16} align="bottom">
                    <Col span={12}>
                      <Form.Item
                        name="diagramsPerPage"
                        label="Diagrams per page:"
                        rules={[
                          {
                            required: true,
                            message: 'This field is required',
                          },
                        ]}
                      >
                        <InputNumber min={1} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        name="padding"
                        label="Space between diagrams (points):"
                        rules={[
                          {
                            required: true,
                            message: 'This field is required',
                          },
                        ]}
                      >
                        <InputNumber min={0} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16} align="bottom">
                    <Col span={8}>
                      <Form.Item name="lightSquares" label="Light square color:">
                        <ColorPicker />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item name="darkSquares" label="Dark square color:">
                        <ColorPicker />
                      </Form.Item>
                    </Col>
                    <Col span={8}>
                      <Form.Item name="borderColor" label="Border color:">
                        <ColorPicker />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item label="Column Layout Rules:">
                    <Space>
                      <Form.Item
                        name="singleColumn"
                        label="Single column if diagrams ≤"
                        noStyle
                      >
                        <InputNumber min={1} />
                      </Form.Item>
                      <Form.Item
                        name="twoColumnMax"
                        label="Two columns if diagrams ≤"
                        noStyle
                      >
                        <InputNumber min={1} />
                      </Form.Item>
                    </Space>
                    <div>
                      <small>Otherwise, three columns will be used.</small>
                    </div>
                  </Form.Item>

                  <Form.Item>
                    <Button type="primary" htmlType="submit" block>
                      Generate PDF
                    </Button>
                  </Form.Item>
                </Form>
              </Spin>
            </Card>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
}

export default App;
