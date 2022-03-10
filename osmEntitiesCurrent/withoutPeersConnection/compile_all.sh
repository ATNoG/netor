#!/bin/bash
cd base && COPYFILE_DISABLE=1 tar -cvz -f ../outputs/5gasp_interdomain_vnf.tar.gz 5gasp_interdomain_vnf
COPYFILE_DISABLE=1 tar -cvz -f ../outputs/5gasp_interdomain_slice_ns_Domain_1.tar.gz 5gasp_interdomain_slice_ns_Domain_1
COPYFILE_DISABLE=1 tar -cvz -f ../outputs/5gasp_interdomain_slice_ns_Domain_2.tar.gz 5gasp_interdomain_slice_ns_Domain_2
cp 5gasp_interdomain_nsst_nst_Domain_1.yml ../outputs/5gasp_interdomain_nsst_nst_Domain_1.yml
cp 5gasp_interdomain_nsst_nst_Domain_2.yml ../outputs/5gasp_interdomain_nsst_nst_Domain_2.yml