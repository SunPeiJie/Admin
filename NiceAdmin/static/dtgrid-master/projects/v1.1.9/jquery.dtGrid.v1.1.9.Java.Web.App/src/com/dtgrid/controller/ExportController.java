package com.dtgrid.controller;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import net.sf.json.JSONObject;

import com.dtgrid.model.Pager;
import com.dtgrid.utils.ExportUtils;
import com.dtgrid.utils.PagerPropertyUtils;

/**
 * dtGrid导出
 * @author 大连首闻科技有限公司
 * @version 1.0
 */
@Controller
@RequestMapping("/dtgrid/export")
public class ExportController {
	
	/**
	 * 执行导出
	 * @param dtGridPager Pager对象
	 * @param request 请求对象
	 * @param response 响应对象
	 * @throws Exception
	 */
	@RequestMapping(value="", method=RequestMethod.POST)
	public void export(String dtGridPager, HttpServletRequest request, HttpServletResponse response) throws Exception {
		Pager pager = PagerPropertyUtils.copy(JSONObject.fromObject(dtGridPager));
		ExportUtils.export(request, response, pager);
	}

}