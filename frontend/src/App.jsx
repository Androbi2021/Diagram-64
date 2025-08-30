import { useState, useRef } from 'react';
import axios from 'axios';
import {
  Layout,
  Form,
  Input,
  InputNumber,
  Button,
  ColorPicker,
  Spin,
  Row,
  Col,
  Card,
  Typography,
  notification,
  Checkbox,
  Modal,
  Space,
} from 'antd';
import { MinusCircleOutlined, PlusOutlined, HolderOutlined } from '@ant-design/icons';
import { DndContext, PointerSensor, useSensor, useSensors, closestCenter } from '@dnd-kit/core';
import {
  SortableContext,
  useSortable,
  arrayMove,
  rectSwappingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

const { Header, Content } = Layout;
const { Title } = Typography;
const { TextArea } = Input;

const fenRegex = /^([rnbqkpRNBQKP1-8]{1,8}\/){7}[rnbqkpRNBQKP1-8]{1,8} [bw] (K?Q?k?q?|-) (-|[a-h][36]) \d+ \d+$/;

const DraggableItem = ({ id, field, remove }) => {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    marginBottom: 8,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes}>
      <Space align="baseline">
        <span {...listeners} style={{ cursor: 'grab' }} role="button" aria-label="Drag to reorder">
          <HolderOutlined />
        </span>
        <Form.Item
          {...field}
          name={[field.name, 'fen']}
          rules={[
            { required: true, message: 'Missing FEN' },
            {
              pattern: fenRegex,
              message: 'Invalid FEN format.',
            }
          ]}
          style={{ width: '100%' }}
        >
          <Input placeholder="FEN" />
        </Form.Item>
        <Form.Item
          {...field}
          name={[field.name, 'description']}
          style={{ width: '100%' }}
        >
          <Input placeholder="Description" />
        </Form.Item>
        <MinusCircleOutlined onClick={() => remove(field.name)} />
      </Space>
    </div>
  );
};

function App() {
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [importText, setImportText] = useState('');
  const [isListExpanded, setIsListExpanded] = useState(false);
  const INITIAL_VISIBLE_COUNT = 4; // Number of items to show when collapsed

  const [form] = Form.useForm();
  const nextId = useRef(0);
  const sensors = useSensors(useSensor(PointerSensor));

  const onDragEnd = ({ active, over }) => {
    if (active && over && active.id !== over.id) {
      const diagrams = form.getFieldValue('diagrams') || [];
      const oldIndex = diagrams.findIndex((item) => item.id === active.id);
      const newIndex = diagrams.findIndex((item) => item.id === over.id);
      if (oldIndex !== -1 && newIndex !== -1) {
        const newDiagrams = arrayMove(diagrams, oldIndex, newIndex);
        form.setFieldsValue({ diagrams: newDiagrams });
      }
    }
  };

  const handleGeneratePdf = async (values) => {
    const fenData = values.diagrams
      .map(({ fen, description }) => ({ fen, description: description || '' }))
      .filter(d => d.fen && d.fen.trim() !== '');

    if (fenData.length === 0) {
      notification.error({
        message: 'Validation Error',
        description: 'Please enter at least one FEN string.',
      });
      return;
    }

    setLoading(true);

    const getColorString = (colorValue) => {
      if (typeof colorValue === 'object' && colorValue !== null && typeof colorValue.toHexString === 'function') {
        return colorValue.toHexString();
      }
      return colorValue;
    };

    const payload = {
      fens: fenData,
      diagrams_per_page: values.diagramsPerPage,
      padding: {
        top: values.padding,
        bottom: values.padding,
        left: values.padding,
        right: values.padding,
      },
      board_colors: {
        light_squares: getColorString(values.lightSquares),
        dark_squares: getColorString(values.darkSquares),
        border_color: getColorString(values.borderColor),
      },
      inner_border_color: getColorString(values.innerBorderColor),

      columns_for_diagrams_per_page: {
        single_column: values.singleColumn,
        two_column_max: values.twoColumnMax,
      },
      title: values.title,
      show_turn_indicator: values.showTurnIndicator,
      show_page_numbers: values.showPageNumbers,
      show_coordinates: values.showCoordinates,
    };

    try {
      const response = await axios.post('/api/generate-pdf/', payload, {
        responseType: 'blob',
      });

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
      let errorMessage = 'An unexpected error occurred.';
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error;
      } else if (err.message) {
        errorMessage = err.message;
      }

      notification.error({
        message: 'Error Generating PDF',
        description: errorMessage,
        duration: 10,
      });

      console.error('Full error object:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#e4e1e1ff' }}>
      <Header style={{ background: '#0d5ba5ff', padding: '0 24px' }}>
        <Title level={2} style={{ color: 'white', lineHeight: '64px', margin: 0 }}>
          Diagram 64
        </Title>
      </Header>
      <Content style={{ padding: '24px' }}>
        <Row justify="center">
          <Col xs={24} sm={20} md={20} lg={20} xl={20}>
            <Card>
              <Spin spinning={loading} tip="Generating PDF...">
                <Form
                  form={form}
                  layout="vertical"
                  onFinish={handleGeneratePdf}
                  initialValues={{
                    title: '',
                    diagrams: [{ fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', description: 'Initial position', id: 'initial-0' }],
                    diagramsPerPage: 6,
                    padding: 2.5,
                    lightSquares: '#ffffffff',
                    darkSquares: '#878787',
                    borderColor: '#ffffffff',
                    innerBorderColor: '#878787',
                    singleColumn: 1,
                    twoColumnMax: 8,
                    showTurnIndicator: true,
                    showPageNumbers: true,
                    showCoordinates: false,
                  }}
                >
                  <Form.Item
                    name="title"
                    label="Enter the title of your PDF (facultative):"
                    rules={[{ required: false}]}
                  >
                    <TextArea
                      rows={1}
                      placeholder="My PDF title"
                      style={{ fontFamily: "Arial" }}
                    />
                  </Form.Item>

                  <Form.List name="diagrams">
                    {(fields, { add, remove }) => {
                      const visibleFields = isListExpanded ? fields : fields.slice(0, INITIAL_VISIBLE_COUNT);

                      return (
                        <>
                          <DndContext sensors={sensors} onDragEnd={onDragEnd} collisionDetection={closestCenter}>
                            <SortableContext
                              items={form.getFieldValue('diagrams')?.map(i => i.id) || []}
                              strategy={rectSwappingStrategy}
                            >
                              <Row gutter={[16, 0]}>
                                {visibleFields.map((field, index) => {
                                  const diagram = form.getFieldValue('diagrams')[index];
                                  return (
                                    <Col xs={24} lg={12} key={field.key}>
                                      <DraggableItem
                                        key={diagram?.id}
                                        id={diagram?.id}
                                        field={field}
                                        remove={remove}
                                      />
                                    </Col>
                                  );
                                })}
                              </Row>
                            </SortableContext>
                          </DndContext>

                          {fields.length > INITIAL_VISIBLE_COUNT && (
                            <Button
                              type="link"
                              onClick={() => setIsListExpanded(!isListExpanded)}
                              style={{ paddingLeft: 0, marginTop: 8 }}
                            >
                              {isListExpanded ? 'Afficher moins' : `Afficher les ${fields.length - INITIAL_VISIBLE_COUNT} autres...`}
                            </Button>
                          )}

                          <Form.Item style={{ marginTop: '16px' }}>
                            <Space>
                              <Button
                                type="dashed"
                                onClick={() => add({ fen: '', description: '', id: `new-${nextId.current++}` })}
                                icon={<PlusOutlined />}
                              >
                                Add Diagram
                              </Button>
                              <Button onClick={() => setIsModalVisible(true)}>
                                Import from Text
                              </Button>
                            </Space>
                          </Form.Item>
                        </>
                      );
                    }}
                  </Form.List>

                  <Modal
                    title="Import Diagrams"
                    open={isModalVisible}
                    onOk={() => {
                      const lines = importText.split('\n').filter(line => line.trim() !== '');
                      const newDiagrams = lines.map((line) => {
                        const parts = line.split(/ \/\/ (.*)/s);
                        return {
                          fen: parts[0],
                          description: parts[1] || '',
                          id: `imported-${nextId.current++}`,
                        };
                      });
                      form.setFieldsValue({ diagrams: newDiagrams });
                      setIsModalVisible(false);
                      setImportText('');
                    }}
                    onCancel={() => setIsModalVisible(false)}
                  >
                    <TextArea
                      rows={10}
                      placeholder="e.g., rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 // Anand vs Carlsen, 2013"
                      value={importText}
                      onChange={(e) => setImportText(e.target.value)}
                      style={{ fontFamily: "'Courier New', Courier, monospace" }}
                    />
                  </Modal>

                  <Row gutter={16}>
                    <Col xs={24} sm={12}>
                      <Form.Item name="diagramsPerPage" label="Diagrams per page:" rules={[{ required: true }]}>
                        <InputNumber min={1} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col xs={24} sm={12}>
                      <Form.Item name="padding" label="Space between diagrams (pt):" rules={[{ required: true }]}>
                        <InputNumber min={0} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Row gutter={16}>
                    <Col xs={6}>
                      <Form.Item name="lightSquares" label="Light squares">
                        <ColorPicker showText />
                      </Form.Item>
                    </Col>
                    <Col xs={6}>
                      <Form.Item name="darkSquares" label="Dark squares">
                        <ColorPicker showText />
                      </Form.Item>
                    </Col>
                    <Col xs={6}>
                      <Form.Item name="borderColor" label="Border">
                        <ColorPicker showText />
                      </Form.Item>
                    </Col>
                    <Col xs={6}>
                      <Form.Item name="innerBorderColor" label="Inner Border">
                        <ColorPicker showText />
                      </Form.Item>
                    </Col>
                  </Row>
                  
                  <Typography.Text strong>Column Layout Rules</Typography.Text>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item name="singleColumn" label="Single column if ≤" tooltip="Max diagrams for a single-column layout.">
                        <InputNumber min={1} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item name="twoColumnMax" label="Two columns if ≤" tooltip="Max diagrams for a two-column layout.">
                        <InputNumber min={1} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item name="showTurnIndicator" valuePropName="checked" style={{ marginTop: '16px' }}>
                    <Checkbox>Show turn indicator for Black</Checkbox>
                  </Form.Item>

                  <Form.Item name="showPageNumbers" valuePropName="checked" style={{ marginTop: '16px' }}>
                    <Checkbox>Show page numbers</Checkbox>
                  </Form.Item>

                  <Form.Item name="showCoordinates" valuePropName="checked" style={{ marginTop: '16px' }}>
                    <Checkbox>Show Coordinates</Checkbox>
                  </Form.Item>

                  <Form.Item style={{ marginTop: '24px' }}>
                    <Button type="primary" htmlType="submit" block loading={loading} size="large">
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