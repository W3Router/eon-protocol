# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: computation.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'computation.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11\x63omputation.proto\x12\x03\x65on\"H\n\x12\x43omputationRequest\x12\x0f\n\x07\x64\x61ta_id\x18\x01 \x01(\t\x12\x11\n\toperation\x18\x02 \x01(\t\x12\x0e\n\x06params\x18\x03 \x01(\x0c\"6\n\x13\x43omputationResponse\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\x0e\n\x06status\x18\x02 \x01(\t\"$\n\x11TaskStatusRequest\x12\x0f\n\x07task_id\x18\x01 \x01(\t\"i\n\x12TaskStatusResponse\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\x0e\n\x06status\x18\x02 \x01(\t\x12\x10\n\x08progress\x18\x03 \x01(\x02\x12\x11\n\tresult_id\x18\x04 \x01(\t\x12\r\n\x05\x65rror\x18\x05 \x01(\t2\x9e\x01\n\x12\x43omputationService\x12\x46\n\x11SubmitComputation\x12\x17.eon.ComputationRequest\x1a\x18.eon.ComputationResponse\x12@\n\rGetTaskStatus\x12\x16.eon.TaskStatusRequest\x1a\x17.eon.TaskStatusResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'computation_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_COMPUTATIONREQUEST']._serialized_start=26
  _globals['_COMPUTATIONREQUEST']._serialized_end=98
  _globals['_COMPUTATIONRESPONSE']._serialized_start=100
  _globals['_COMPUTATIONRESPONSE']._serialized_end=154
  _globals['_TASKSTATUSREQUEST']._serialized_start=156
  _globals['_TASKSTATUSREQUEST']._serialized_end=192
  _globals['_TASKSTATUSRESPONSE']._serialized_start=194
  _globals['_TASKSTATUSRESPONSE']._serialized_end=299
  _globals['_COMPUTATIONSERVICE']._serialized_start=302
  _globals['_COMPUTATIONSERVICE']._serialized_end=460
# @@protoc_insertion_point(module_scope)
